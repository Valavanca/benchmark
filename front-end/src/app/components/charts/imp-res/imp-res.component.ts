import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';

// Service
import { MainSocketService } from '../../../core/services/main.socket.service';

import { Solution } from '../../../data/taskData.model';
import { MainEvent } from '../../../data/client-enums';

interface PointExp {
  configuration: any;
  result: any;
  time: any;
} 

@Component({
  selector: 'imp-res',
  templateUrl: './imp-res.component.html',
  styleUrls: ['./imp-res.component.scss']
})
export class ImpResComponent implements OnInit {
  // The experements results
  bestRes = new Set<PointExp>()
  allRes = new Set<PointExp>()
  // Best point 
  solution: Solution

  // poiner to DOM element #map
  @ViewChild('improvement') impr: ElementRef;

  constructor(private ioMain: MainSocketService) { }

  ngOnInit() {
    this.initMainEvents();
    window.onresize = () => this.bestRes.size>2 && this.render()
  }
  //                              WebSocket
  // --------------------------   Main-node
  private initMainEvents(): void {

    this.ioMain.onEvent(MainEvent.BEST)
      .subscribe((obj: any) => {
        this.solution = obj['best point']
        let min = new Date().getMinutes()
        let sec = new Date().getSeconds()
        let temp: PointExp = {
          'configuration': obj['best point']['configuration'],
          'result': obj['best point']['result'],
          'time': min + 'm ' + sec + 's'
        } 
        this.allRes.add(temp) 
        this.bestRes.add(temp) // There is no check if this solution is the best decision 
        this.render() // Render chart when all points got
      });
    this.ioMain.onEvent(MainEvent.TASK_RESULT)
      .subscribe((obj: any) => {
        let min = new Date().getMinutes()
        let sec = new Date().getSeconds()
        this.allRes.add({
          'configuration': obj['configuration'],
          'result': obj['result'],
          'time': min + 'm ' + sec + 's'
        }) // Add new point(result)

        let temp: PointExp = {
          'configuration': obj['configuration'],
          'result': obj['result'],
          'time': min + 'm ' + sec + 's'
        } 

        // Check the best available point
        this.bestRes && this.bestRes.forEach(function(resItem){
          if (temp.result > resItem.result) {
            temp.result = resItem.result
            temp.configuration = resItem.configuration
          }
        })  
        this.bestRes.add(temp) // Add the best available point(result)
        this.bestRes.size>2 && this.render()
      });
    this.ioMain.onEvent(MainEvent.MAIN_CONF)
      .subscribe((obj: any) => {
        this.bestRes.clear()
        this.allRes.clear()
        this.solution = undefined
      });
  }

  render() {
    // DOM element. Render point
    const element = this.impr.nativeElement

    // X-axis data
    const xBest = Array.from(this.bestRes).map(i => i["time"]);
    // Results
    const yBest = Array.from(this.bestRes).map(i => i["result"]);
    
    var allResultSet = { // Data for all results
      x: Array.from(this.allRes).map(i => i["time"]),
      y: Array.from(this.allRes).map(i => i["result"]),
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'rgba(67,67,67,1)', width: 1, shape: 'spline', dash: 'dot' },
      text: Array.from(this.allRes).map(i => String(i["configuration"])),
      marker: {
        color: 'rgba(255,64,129,1)',
        size: 8,
        symbol: 'x'
      },
      name: 'results'
    }
    var bestPointSet = { // Data for the best available results 
      x: xBest,
      y: yBest,
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: 'rgba(67,67,67,1)', width: 2, shape: 'spline' },
      name: 'best point',
      marker: { size: 6, symbol: 'x', color: 'rgba(67,67,67,1)' }
    }

    var startEndPoint = { // Start & Finish markers
      x: [xBest[0], xBest[xBest.length - 1]],
      y: [yBest[0], yBest[yBest.length - 1]],
      type: 'scatter',
      mode: 'markers',
      hoverinfo: 'none',
      showlegend: false,
      marker: { color: 'rgba(255,64,129,1)', size: 10 }
    }

    let data = [allResultSet, bestPointSet, startEndPoint];

    var layout = {
      title: 'The best results in time',
      showlegend: true,
      autosize: true,
      xaxis: {
        title: "Time",
        showline: true,
        showgrid: false,
        showticklabels: true,
        linecolor: 'rgb(204,204,204)',
        linewidth: 2,
        autotick: false,
        ticks: 'outside',
        tickcolor: 'rgb(204,204,204)',
        tickwidth: 2,
        ticklen: 5,
        tickfont: {
          family: 'Roboto',
          size: 12,
          color: 'rgb(82, 82, 82)'
        }
      },
      yaxis: {
        title: "Energy",
        showgrid: false,
        zeroline: false,
        showline: true,
        linecolor: 'rgb(204,204,204)',
        showticklabels: true,
        ticks: 'outside',
        tickcolor: 'rgb(204,204,204)',
        ticklen: 5,
        tickfont: {
          family: 'Roboto',
          size: 12,
          color: 'rgb(82, 82, 82)'
        }

      },
      // margin: {
      //   autoexpand: false,
      //   l: 100,
      //   r: 20,
      //   t: 100
      // },
      // annotations: [
        // {
        //   xref: 'paper',
        //   yref: 'paper',
        //   x: 0.05,
        //   y: 1.05,
        //   xanchor: 'center',
        //   yanchor: 'bottom',
        //   text: 'Best results for time',
        //   font: {
        //     family: 'Roboto',
        //     size: 20,
        //     color: 'rgb(37,37,37)'
        //   },
        //   showarrow: false
        // },
        // {
        //   xref: 'paper',
        //   yref: 'paper',
        //   x: 0.5,
        //   y: -0.1,
        //   xanchor: 'center',
        //   yanchor: 'top',
        //   text: 'Time',
        //   showarrow: false,
        //   font: {
        //     family: 'Roboto',
        //     size: 15,
        //     color: 'rgb(150,150,150)'
        //   }
        // }
      // ]
    };

    Plotly.react(element, data, layout);
  }

}