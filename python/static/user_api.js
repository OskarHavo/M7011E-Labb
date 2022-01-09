function genTimeChart(chartName,minimum,maximum) {
	return new Chart(chartName, {
		type: "line",
		data: {
			labels: [],
			datasets: [{
				label: "Consumption",
				fill: false,
				backgroundColor: "rgb(0,0,255,1.0)",
				borderColor: "rgb(200,192,80)",
				pointBackgroundColor: 'rgba(180,172,60,0.3)',
				tension:0.2,
				data: []
			},
			{
				label:"Production",
				fill: false,
				backgroundColor: "rgb(0,0,255,1.0)",
				borderColor: "rgb(20,30,100)",
				pointBackgroundColor: 'rgba(30,50,120,0.3)',
				tension:0.2,
				data: []
			}]
		},
		options: {
			plugins: {
				legend: {
					position: 'top',
				},
			},
			scales: {
				yAxes: [{ticks: {min: 0, max:maximum}}],
			}
		}
	});
}

function genHistoryChart(chartName) {
	return new Chart(chartName, {
		type: "bar",
		data: {
			labels: [],
			datasets: [{
				label: "Consumption",
				fill: false,
				backgroundColor: "rgb(255,0,0,1.0)",
				borderColor: "rgb(200,192,80)",
				pointBackgroundColor: 'rgba(180,172,60,0.3)',
				//tension:0.2,
				data: []
			},
			{
				label:"Production",
				fill: false,
				backgroundColor: "rgb(0,255,0,1.0)",
				borderColor: "rgb(20,30,100)",
				pointBackgroundColor: 'rgba(30,50,120,0.3)',
				//tension:0.2,
				data: []
			},
			{
				label:"Price",
				fill: false,
				backgroundColor: "rgb(0,0,255,1.0)",
				borderColor: "rgb(20,255,100)",
				pointBackgroundColor: 'rgba(20,255,40,0.3)',
				//tension:0.2,
				data: []
			}]
		},
		options: {
			plugins: {
				legend: {
					position: 'top',
				},
			},
			scales: {
				yAxes: [{
                display: true,
                ticks: {
                    beginAtZero: true
                }
            }]
			}
		}
	});
}

function addData(chart, label, data) {
	chart.data.labels.push(label);
	var i = 0;
	chart.data.datasets.forEach((dataset) => {
		console.log(data["Consumption"]);
		dataset.data.push(data[i]);
		i ++;
	});

}
function removeFirst(chart) {
	chart.data.labels.shift();
	chart.data.datasets.forEach((dataset) => {
		dataset.data.shift();
	});

}

const request = ( url, params = {}, method = 'GET' ) => {
	let options = {
		method,
		headers: {
			'Content-Type': 'application/json'
		},
	};
	if ( 'GET' === method ) {
		url += '?' + ( new URLSearchParams( params ) ).toString();
	} else {
		options.body = JSON.stringify( params );
	}

	return fetch( url, options ).then( response => response.json() );
};

var simData = [];
var trailLength = 10;

const post = (url, params) => request(url,params,'GET');
const put = (url,params) => request(url,params,"PUT");

function updateGraph(chart,bufferSize=10) {
	if (simData.length > 0) {
		var data = simData[simData.length - 1];

		var d = new Date(data.timestamp+"Z");
		chart.data.labels.push(d.getUTCHours()+":"+d.getUTCMinutes()+":"+d.getUTCSeconds());
		chart.data.datasets[0].data.push(data["consumption"]);
		chart.data.datasets[1].data.push(data["production"]);

		if (chart.data.labels.length > bufferSize) {
			removeFirst(chart);
		}
		var maximum = Math.max.apply(null, chart.data.datasets[0].data);
		var prodMax = Math.max.apply(null, chart.data.datasets[1].data);
		if (prodMax > maximum) {
			maximum = prodMax;
		}

		chart.options.scales.yAxes = [{ticks: {min: 0, max: maximum}}];
		chart.update();
	}
}

var buyRatio = 0.5;
var sellRatio = 0.5;
function uploadData(valuename, param) {
	buyRatio = buyRatio + 0.1;
	sellRatio = sellRatio + 0.1;
	put('/fetch', {"valueName":valuename,"data":param}).then(response => {
	});
}

function updateRawSimulatorDataOutput(simulatorData) {

	try {
		timeoutput = "Date: " + simulatorData.timestamp;
		productionoutput = "Production: " + simulatorData.production.substring(0, 4) + "kWh";
		consumptionoutput = "Consumption: " + simulatorData.consumption.substring(0, 4) + "kWh";
		powertoselloutput = "PowerToSell: " + simulatorData.powerToSell.substring(0, 4) + "kWh";
		powertobuyoutput = "PowerToBuy: " + simulatorData.powerToBuy.substring(0, 4) + "kWh";
		bufferoutput = "Buffer: " + simulatorData.buffer.substring(0, 4) + "kWh";
		buyoutput = "Buy Ratio: " + simulatorData.buyRatio.substring(0, 4);
		selloutput = "Sell Ratio: " + simulatorData.sellRatio.substring(0, 4);
		windspeed = "Wind speed: " + simulatorData.windspeed.substring(0, 4) + "m/s";

		dateoutput = String(timeoutput);
		output1 = String(productionoutput + " " + consumptionoutput);
		output2 = String(powertoselloutput + " " + powertobuyoutput + " " + bufferoutput);
		output3 = String(buyoutput + " " + selloutput);
	}catch(error) {
		dateoutput = "No Data";
		output1 = "";
		output2 = "";
		output3 = "";
		output4 = "";
	}
    document.getElementById("rawDataOutput_DATE").innerHTML = dateoutput; //JSON.stringify(output,null,4);
	document.getElementById("rawDataOutput_OUTPUT1").innerHTML = output1;
	document.getElementById("rawDataOutput_OUTPUT2").innerHTML = output2;
	document.getElementById("rawDataOutput_OUTPUT3").innerHTML = output3;

	// Set the text in the top bar
	document.getElementById("datetext").innerHTML = simulatorData.timestamp;

}
function historicalDataRetriever(chart){
	post("fetch",{}).then(data=>{
		var div = document.getElementById("historicaldataoutputdiv");
		console.log(data)

        var output = ""
		for (var i = 0, size = data.history.length; i < size; i++) {
			var currentData = data.history[i];
			chart.data.labels.push(currentData["timestamp"]);
			chart.data.datasets[0].data.push(currentData["consumption"]);
			chart.data.datasets[1].data.push(currentData["production"]);
			chart.data.datasets[2].data.push(currentData["electricityPrice"]);
		}
		chart.update();
	});
}


function updateUserGauges(simulatorData) {

	// Max Value of gauges
	var maxValue = 25.0;
	var maxPriceValue = 50.0;
	var maxValueWindSpeed = 10.0;
	var maxValueNetProduction = 30.0;
	var MaxValueBuffer = 100.0;


	try {
		// First Value is a string showing the formatted value. Used for the string showing the value.
		// Second Value is a string showing the percentage of the total value that the current value is. Used for the gauge.
		consumption = simulatorData.consumption.substring(0, 5);
		consumptionoutput = String((consumption / maxValue) * 100.0);

		production = simulatorData.production.substring(0, 5);
		productionoutput = String((production / maxValue) * 100.0);

		windspeed = String(parseFloat(simulatorData.windspeed)).substring(0, 5);
		windspeedoutput = String((windspeed / maxValueWindSpeed) * 100.0);

		netproduction = String(parseFloat(production) - parseFloat(consumption)).substring(0, 5);
		netproductionoutput = String((Math.abs(netproduction) / maxValueNetProduction) * 100.0).substring(0, 5);

		buffer = simulatorData.buffer.substring(0, 5);
		bufferoutput = String((buffer / MaxValueBuffer) * 100.0);

		currentelectrictyprice = simulatorData.electricityPrice.substring(0, 5);
		currentelectrictypriceoutput = String((currentelectrictyprice / maxPriceValue) * 100.0);

		document.getElementById("usergauge_consumption").style.width = consumptionoutput + "%";
		document.getElementById("usergauge_consumption_text").innerHTML = String(consumption) + "kWh";

		document.getElementById("usergauge_production").style.width = productionoutput + "%";
		document.getElementById("usergauge_production_text").innerHTML = production + "kWh";

		document.getElementById("usergauge_windspeed").style.width = windspeedoutput + "%";
		document.getElementById("usergauge_windspeed_text").innerHTML = windspeed + "m/s";

		document.getElementById("usergauge_netproduction").style.width = netproductionoutput + "%";
		document.getElementById("usergauge_netproduction_text").innerHTML = netproduction + "kWh";

		document.getElementById("usergauge_buffer").style.width = bufferoutput + "%";
		document.getElementById("usergauge_buffer_text").innerHTML = buffer + "kWh";

		document.getElementById("usergauge_price").style.width = currentelectrictypriceoutput + "%";
		document.getElementById("usergauge_price_text").innerHTML = currentelectrictyprice + "kr";

		// Set color to red if negative.
		if (parseFloat(netproduction) < 0.0) {
			document.getElementById("usergauge_netproduction").style.backgroundColor = '#c70000';
		} else {
			document.getElementById("usergauge_netproduction").style.backgroundColor = '#007300';
		}
	} catch(error) {
		consumption = "0.0";
		consumptionoutput = "5.0";
		production = "0.0";
		productionoutput = "5.0";
		windspeed = "0.0";
		windspeedoutput = "5.0";
		netproduction = "0.0";
		netproductionoutput = "2.0";
		buffer = "0.0";
		bufferoutput = "0.0";
		currentelectrictyprice = "0.0";
		currentelectrictypriceoutput = "0.0";
	}
}

// Only Updates once each tick.
function updateUserSliders(simulatorData) {

    var buyRatio = parseFloat(simulatorData.buyRatio)*100;
    document.getElementById("buyingRatioText").innerHTML = buyRatio+"%";
	document.getElementById("buyRatio").value = buyRatio;

    var sellRatio = parseFloat(simulatorData.sellRatio)*100;
	document.getElementById("sellRatio").value = sellRatio;
	if (simulatorData.blocked == "True"){
		document.getElementById("sellingRatioText").innerHTML = "BLOCKED";
		document.getElementById("sellRatio").disabled = true;
	} else {
		document.getElementById("sellRatio").disabled = false;
		document.getElementById("sellingRatioText").innerHTML = sellRatio+"%";
	}

}

document.addEventListener('DOMContentLoaded', (event) => {
	var slider = document.querySelectorAll('.slider');
	slider.item(0).onmouseup = function () {
		uploadData(this.id, parseFloat(this.value) / 100);
		document.getElementById("buyingRatioText").innerHTML = this.value + "%";
	};
	slider.item(1).onmouseup = function () {
		uploadData(this.id, parseFloat(this.value) / 100);
		document.getElementById("sellingRatioText").innerHTML = this.value + "%";
	};
});
