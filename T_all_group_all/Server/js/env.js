
var chart = null;
var hchart = null;

function drawLineChart(start,end) {
	//jsonUrl='/data/env.json'
	if(end==''){
		jsonUrl='/data/env.json?s='+start;
	}
	else{
		jsonUrl='/data/env.json?s='+start+'&e='+end;
	}
	
	var jsonData = $.ajax({
		url: jsonUrl,
		dataType: 'json',
	}).done(function (results) {

		var tempData=[],humiData=[];
		
		results["envdata"].forEach(function(element) {
			

			tempData.push({x:new Date(element.time),y:parseFloat(element.temp)});
			humiData.push({x:new Date(element.time),y:parseFloat(element.humi)});

		});

		// Create the chart.js data structure using 'labels' and 'data'
		var tempData = {
			datasets : [{
				label					: 'Temperature',
				fillColor				: "rgba(151,187,205,0.2)",
				strokeColor				: "rgba(151,187,205,1)",
				pointColor				: "rgba(151,187,205,1)",
				pointStrokeColor		: "#fff",
				pointHighlightFill		: "#fff",
				pointHighlightStroke	: "rgba(151,187,205,1)",
				data					: tempData
			}]
		};
		
		var humiData = {
			datasets : [{
				label					: 'Humidity',
				fillColor				: "rgba(151,187,205,0.2)",
				strokeColor				: "rgba(151,187,205,1)",
				pointColor				: "rgba(151,187,205,1)",
				pointStrokeColor		: "#fff",
				pointHighlightFill		: "#fff",
				pointHighlightStroke	: "rgba(151,187,205,1)",
				data					: humiData
			}]
		};

		// Get the context of the canvas element we want to select
		var ctx = document.getElementById("temp-canvas").getContext("2d");
		var hctx = document.getElementById("humi-canvas").getContext("2d");
		// Instantiate a new chart
		//var myLineChart = new Chart(ctx).Line(tempData);
		var config = {
			type: 'line',
			data: tempData,
			options: {
				title: {
					display: false,
					text: 'Temperature Table'
				},
				scales: {
					yAxes: [{
						scaleLabel: {
							display: true,
							labelString: 'Temperature(℃)'
						}
						
					}],
					xAxes: [{
						type: 'time',
						//time: {
						//	unit: 'minute',
						//	unitStepSize: 5,
						//	displayFormats: {
						//		'minute': 'LLL'
						//	}
						//},
						scaleLabel: {
							display: false,
							labelString: 'Time'
						}
						
					}]
				}
			}
		};
		var hconfig = {
			type: 'line',
			data: humiData,
			options: {
				title: {
					display: false,
					text: 'Humidity'
				},
				scales: {
					yAxes: [{
						scaleLabel: {
							display: true,
							labelString: 'Humidity(%)'
						}
						
					}],
					xAxes: [{
						type: 'time',
						//time: {
						//	unit: 'minute',
						//	unitStepSize: 5,
						//	displayFormats: {
						//		'minute': 'LLL'
						//	}
						//},
						scaleLabel: {
							display: false,
							labelString: 'Time'
						}
						
					}]
				}
			}
		};
		
		if(chart != null){
			chart.destroy();
		}
		if(hchart != null){
			hchart.destroy();
		}
		chart = new Chart(ctx, config);
		hchart = new Chart(hctx, hconfig);
	});
}



drawLineChart('2019-04-12T00:00','2019-04-12T23:59');

function drawEnvChartByInput(){
	var start=document.getElementById("start").value;
	var end=document.getElementById("end").value;
	drawLineChart(start,end);
}

document.getElementById("show").addEventListener("click", drawEnvChartByInput);