from repeater.history import History

def test_default_history():
    def_history = History().history
    assert def_history == {}

def test_get():
    points = [(2400, 2), (0, 1), (500.09, 25.8), ("qwe", "hjk"), ("sdf", 25), (500, "fgh"), ()]
    values = [[45, 68, 56], ["wer", 567, 345.7], 56, "fhgh", ["rty", "dfg"], 45.8, []]
    history1 = History()
    for p,v in zip(points,values):
        history1.put(p, v)
    for i in range(len(values)):
        values[i] = [values[i]]
        assert history1.get(points[i]) == values[i]


def test_put():
    point1 = (2900, 32)
    values1 = [1, 50]
    history1 = History()
    history1.put(point1, values1[0])
    history1.put(point1, values1[1])
    assert history1.history[str(point1)] == values1
    history1.history = {}
    points = [(2900, 32), (3000, 48), "123", 0, (3000, 32), [2900, 32], [2900, 16]]
    values = [50, "yui", "ret", 5, [55, 48, 99], 1, ["123", 123]]
    for p,v in zip(points,values):
        history1.put(p, v)
    for i in range(len(points)):
        values[i] = [values[i]]
        assert history1.history[str(points[i])] == values[i]

# TODO - test "dump" function (write to file)
