
var chart = null;
var hchart = null;

var latestTime = '1970-01-01 00:00:01'

function updateData(){
	var jsonUrl='/data/env_live.json?s='+latestTime
	

	var jsonData = $.ajax({
		url: jsonUrl,
		dataType: 'json',
	}).done(function (results) {
		
		results["envdata"].forEach(function(element) {
			
			if(Date.parse(element.time)>Date.parse(latestTime)){
				latestTime=element.time
				//document.getElementById("demo").innerHTML = latestTime
			}
			
			chart.data.datasets.forEach((dataset) => {
				dataset.data.push({x:new Date(element.time),y:parseFloat(element.temp)});
				if(dataset.data.length>30){
					dataset.data.shift();
				}
				
			});
			hchart.data.datasets.forEach((dataset) => {
				dataset.data.push({x:new Date(element.time),y:parseFloat(element.humi)});
				if(dataset.data.length>30){
					dataset.data.shift();
				}
			});
		
		});
		chart.update();
		hchart.update();

		// Create the chart.js data structure using 'labels' and 'data'

		
	

		
	});
}

function drawLineChart(start_time) {
	var jsonUrl='/data/env_live.json?s'+start_time
	

	var jsonData = $.ajax({
		url: jsonUrl,
		dataType: 'json',
	}).done(function (results) {

		var tempData=[], humiData=[];
		
		results["envdata"].forEach(function(element) {

			if(Date.parse(element.time)>Date.parse(latestTime)){
				latestTime=element.time
			}
			
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
						distribution: 'series'
						//time: {
						//	unit: 'minute',
						//	unitStepSize: 1,
						//	displayFormats: {
						//		'minute': 'LLL'
						//	}
						//},
						//scaleLabel: {
						//	display: false,
						//	labelString: 'Time'
						//}
						
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
						distribution: 'series'
						//time: {
						//	unit: 'minute',
						//	unitStepSize: 1,
						//	displayFormats: {
						//		'minute': 'LLL'
						//	}
						//},
						//scaleLabel: {
						//	display: false,
						//	labelString: 'Time'
						//}
						
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



drawLineChart(moment().subtract(1, 'h').format('YYYY/MM/DD HH:mm:ss'));


document.getElementById("show").addEventListener("click", updateData);

setInterval(updateData, 3000);