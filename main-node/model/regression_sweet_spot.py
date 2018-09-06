from sklearn import model_selection
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

from functools import reduce

from model.model_abs import Model
from tools.features_tools import split_features_and_labels


class RegressionSweetSpot(Model):
    def __init__(self, log_file_name, test_size, features, labels):
        """
        Initialization of regression model. It will
        :param log_file_name: - string, location of file, which will store results of model creation
        :param test_size: float number, displays size of test data set
        :param features:  features in machine learning meaning selected by Sobol
                          TODO - shape of features
        :param labels: labels in machine learning meaning selected by Sobol
                       TODO - shape of labels
        """
        self.test_size = test_size
        self.all_features = features
        self.all_labels = labels
        self.log_file_name = log_file_name
        self.model = None
        self.accuracy = 0
        self.solution_ready = False
        self.solution_features = None
        self.solution_labels = None

    def build_model(self, degree=6, score_min=0.85, tries=20):
        """
        Return False, if it is impossible to build the model, and True, if the model was built successfully
        :param degree:
        :param score_min:
        :param tries:
        :return: True or False
        """
        cur_accuracy = 0.99
        best_got = -10e10
        best_model = None
        init_test_size = self.test_size
        while cur_accuracy > score_min:
            self.test_size = init_test_size
            while self.test_size > 0.3:
                for x in range(tries):
                    self.resplit_data()
                    model = Pipeline([('poly', PolynomialFeatures(degree=degree, interaction_only=False)),
                                      ('reg', Ridge())])
                    model.fit(self.feature_train, self.target_train)
                    score_measured = model.score(self.feature_test, self.target_test)

                    if score_measured > best_got:
                        best_got = score_measured
                        best_model = model
                        temp_message = ('GOT NEW ACCURACY: %s with %s test size and %s accuracy threshold ' % (
                            round(score_measured, 3), round(self.test_size, 2), round(cur_accuracy, 2)))
                        print(temp_message)

                    # print("Accuracy: %s, test size: %s, try: %s" % (cur_accuracy, test_size, x))
                if best_got > cur_accuracy:
                    self.model = best_model
                    self.accuracy = best_got
                    print("Regression model built with %s test size and %s accuracy." % (
                        self.test_size, self.accuracy))
                    return True
                else:
                    self.test_size -= 0.01
            cur_accuracy -= 0.01
        print("Unable to build model, current best accuracy: %s need more data.." % best_got)
        return False

    def validate_model(self, io, search_space, degree=6):
        """
        Return True, if the model have built, and False, if the model can not build or the model already exists
        :param io: id using for web-sockets
        :param search_space: list of dimensions for this experiment
                             shape - list of lists, e.g. ``[[1, 2, 4, 8, 16, 32], [1200.0, 1300.0, 2700.0, 2900.0]]``
                                     if there is such search space in "taskData.json" :
                                         {
                                             "threads": [1, 2, 4, 8, 16, 32],
                                             "frequency": [1200.0, 1300.0, 2700.0, 2900.0]
                                         }
        :param degree:
        :return: True or False
        """
        # Check if model was built.
        if not self.model:
            return False

        self.test_model_all_data(search_space)

        # Check if the model is adequate - write it.
        predicted_labels, predicted_features = self.predict_solution(io, search_space)
        if predicted_labels[0] >= 0:
            f = open(self.log_file_name, "a")
            f.write("Search space::\n")
            f.write(str(search_space) + "\n")
            f.write("Testing size = " + str(self.test_size) + "\n")
            # f.write("Degree = " + str(degree)+ "\n")
            for i in range(degree+1):
                if i == 0:
                    f.write("(TR ^ 0) * (FR ^ 0) = " + str(self.model.named_steps['reg'].coef_[i]) + "\n")
                else:
                    for j in range(i+1):
                        f.write("(TR ^ " + str(i - j) + ") * (FR ^ " + str(j) + ") = " + \
                                str(self.model.named_steps['reg'].coef_[0][self.sum_fact(i)+j])+ "\n")
            f.write("R^2 = " + str(self.model.score(self.feature_test, self.target_test))+"\n")
            f.write("Intercept = " + str(self.model.named_steps['reg'].intercept_)+"\n")
            f.close()
            self.solution_ready = True
            print("Built model is valid.")
            if io:
                io.emit('info', {'message': "Built model is valid"})
            return True
        else:
            self.solution_ready = False
            print("Predicted energy lower than 0: %s. Need more data.." % predicted_labels[0])
            return False

    def predict_solution(self, io, search_space):
            """
            Takes features, using previously created model makes regression to find labels
            and return label with the lowest value.
            :param search_space: list of data points (each data point is also a list).
            :param io: id using for web-sockets
            :return: lowest value, and related features.
            """
            predictions = [[label, index] for (index, label) in enumerate(self.model.predict(search_space))]

            if io:
                all_predictions = [{'configuration': search_space[index], "prediction": round(prediction[0], 2)}
                                   for (prediction, index) in predictions]
                io.emit('regression', {"regression": all_predictions})

            label, index = min(predictions)
            return label, search_space[index]

    def validate_solution(self, io, task_config, repeater, default_value, predicted_features):
        # validate() in regression
        print("Verifying solution that model gave..")

        if io:
            io.emit('info', {'message': "Verifying solution that model gave.."})

        solution_candidate = repeater.measure_task([predicted_features], io=io)
        solution_feature, solution_labels = split_features_and_labels(solution_candidate,
                                                                      task_config["FeaturesLabelsStructure"])
        # If our measured energy higher than default best value - add this point to data set and rebuild model.
        # validate false
        if solution_labels > default_value:
            print("Predicted energy larger than default.")
            print("Predicted energy: %s. Measured: %s. Default configuration: %s" %(
                predicted_features[0], solution_labels[0][0], default_value[0][0]))
            prediction_is_final = False
        else:
            print("Solution validation success!")

            if io:
                io.emit('info', {'message': "Solution validation success!"})

            prediction_is_final = True
        self.solution_labels = solution_labels[0]
        self.solution_features = solution_feature[0]
        return self.solution_labels, prediction_is_final

    def resplit_data(self):
        """
        Just recreates subsets of features and labels for training and testing from existing features and labels.
        :return: None
        """
        self.feature_train, self.feature_test, self.target_train, self.target_test = \
            model_selection.train_test_split(self.all_features, self.all_labels, test_size=self.test_size)

    @staticmethod
    def sum_fact(num):
        """
        Return the sum of all numbers from 1 till 'num'
        :param num: int
        :return:
        """
        return reduce(lambda x, y: x+y, list(range(1, num + 1)))

    def test_model_all_data(self, search_space):
        """

        :param search_space: list of dimensions for this experiment
                             shape - list of lists, e.g. ``[[1, 2, 4, 8, 16, 32], [1200.0, 1300.0, 2700.0, 2900.0]]``
                                     if there is such search space in "taskData.json" :
                                         {
                                             "threads": [1, 2, 4, 8, 16, 32],
                                             "frequency": [1200.0, 1300.0, 2700.0, 2900.0]
                                         }
        """
        from tools.features_tools import split_features_and_labels
        from tools.initial_config import load_task
        from tools.splitter import Splitter
        all_data = []

        file_path = "./csv/" + load_task()["ExperimentsConfiguration"]["WorkerConfiguration"]["ws_file"]
        spl = Splitter(file_path)
        for point in self.all_features:
            if point in search_space:
                search_space.remove(point)
        for point in search_space:
            spl.search(str(point[0]), str(point[1]))
            all_data += [[float(x['FR']), int(x['TR']), float(x['EN'])] for x in spl.new_data]
        features, labels = split_features_and_labels(all_data, ['feature', 'feature', 'label'])
        # from sklearn.model_selection import train_test_split
        score = self.model.score(features, labels)

        temp_message = ("FULL MODEL SCORE: %s. Measured with %s points" % (str(score), str(len(features))))
        print(temp_message)

    def get_result(self, repeater, features, labels, io):
        """

        :param repeater:
        :param features: list of all currently discovered features.
                         TODO - shape of features
        :param labels: list of all currently discovered labels.
                       TODO - shape of labels
        :param io: id using for web-sockets
        :return: solution_labels, solution_features
        """
        #   In case, if regression predicted final point, that have less energy consumption, that default, but there is
        # point, that have less energy consumption, that predicted - report this point instead predicted.

        print("\n\nFinal report:")

        if not self.solution_labels:
            temp_message = "Optimal configuration was not found. Reporting best of the measured."
            print(temp_message)
            self.solution_labels = min(labels)
            index_of_the_best_labels = self.all_labels.index(self.solution_labels)
            self.solution_features = self.all_features[index_of_the_best_labels]
            if io:
                io.emit('info', {'message': temp_message, "quality": self.solution_labels,
                                 "conf": self.solution_features})

        elif min(labels) < self.solution_labels:
            temp_message = ("Configuration(%s) quality(%s), \
                             \nthat model gave worse that one of measured previously, but better than default.\
                             \nReporting best of measured." %
                            (self.solution_features, self.solution_labels))
            print(temp_message)
            if io:
                io.emit('info', {'message': temp_message, "quality": self.solution_labels,
                                 "conf": self.solution_features})

            self.solution_labels = min(labels)
            index_of_the_best_labels = self.all_labels.index(self.solution_labels)
            self.solution_features = self.all_features[index_of_the_best_labels]

        print("ALL MEASURED FEATURES:\n%s" % str(features))
        print("ALL MEASURED LABELS:\n%s" % str(labels))
        print("Number of measured points: %s" % len(self.all_features))
        print("Number of performed measurements: %s" % repeater.performed_measurements)
        print("Best found energy: %s, with configuration: %s" % (self.solution_labels, self.solution_features))

        if io:
            configuration = [float(self.solution_features[0]), int(self.solution_features[1])]
            value = round(self.solution_labels[0], 2)
            temp = {
                'best point': {
                    'configuration': configuration,
                    'result': value,
                    'measured points': self.all_features
                }
            }
            io.emit('best point', temp)

        return self.solution_labels, self.solution_features
