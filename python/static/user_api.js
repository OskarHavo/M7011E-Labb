function genTimeChart(chartName,minimum,maximum) {
	return new Chart(chartName, {
		type: "line",
		data: {
			labels: [],
			datasets: [{
				fill: false,
				backgroundColor: "rgb(0,0,255,1.0)",
				borderColor: "rgb(200,192,80)",
				pointBackgroundColor: 'rgba(180,172,60,0.3)',
				tension:0.2,
				data: []
			}]
		},
		options: {
			legend: {display: false},
			scales: {
				yAxes: [{ticks: {min: 0, max:maximum}}],
			}
		}
	});
}

//var chart = genTimeChart("mychart",-20,20);
function addData(chart, label, data) {
	chart.data.labels.push(label);
	chart.data.datasets.forEach((dataset) => {
		dataset.data.push(data);
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
		headers:{'Accept': 'application/json',
         'Content-Type': 'application/json'}
	};
	if ( 'GET' === method ) {
		url += '?' + ( new URLSearchParams( params ) ).toString();
	} else {
		options.body = JSON.stringify( params );
	}

	return fetch( url, options ).then( response => response.json() );
};

var simData = [];
var trailLength = 2;

function fetchDataCycle() {
	post('/fetch', {}).then(response => {
		if (simData.length== 0 || simData[simData.length - 1]["timestamp"] != response["timestamp"]) {
			simData.push(response)
			if (simData.length > trailLength) {
				simData.slice(1, simData.length)
			}
			console.log(simData[simData.length - 1])
		}
	});
}

const post = (url, params) => request(url,params,'GET');
const put = (url,params) => request(url,params,"PUT");
var k = 0
//var repeater;

function updateGraph(chart,startx,starty,bufferSize=10) {
	if (simData.length > 0) {
		var i = k;
		k = k + 1;
		var data = simData[simData.length - 1]["consumption"];
		addData(chart, i, data);
		if (chart.data.labels.length > bufferSize) {
			removeFirst(chart);
		}
		var maximum = Math.max.apply(null, chart.data.datasets[0].data);
		chart.options.scales.yAxes = [{ticks: {min: 0, max: maximum}}];
		startx++;
		starty += Math.floor(Math.random() * 10) - 4;
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

    if (simulatorData  == null){
        dateoutput = "No Data";
        output1 = "";
        output2 = "";
        output3 = "";
    }else{
        timeoutput = "Date: " + simulatorData.timestamp;
        productionoutput = "Production: " + simulatorData.production.substring(0,4) +"kWh" ;
        consumptionoutput = "Consumption: " + simulatorData.consumption.substring(0,4) +"kWh";
        powertoselloutput = "PowerToSell: " + simulatorData.powerToSell.substring(0,4) +"kWh";
        powertobuyoutput = "PowerToBuy: " + simulatorData.powerToBuy.substring(0,4) +"kWh";
        bufferoutput  = "Buffer: "+  simulatorData.buffer.substring(0,4) +"kWh";
        buyoutput  = "Buy Ratio: " +  simulatorData.buyRatio.substring(0,4);
        selloutput  = "Sell Ratio: " +  simulatorData.sellRatio.substring(0,4);

        dateoutput = String(timeoutput);
        output1 = String(productionoutput + " " +  consumptionoutput);
        output2 = String(powertoselloutput + " " + powertobuyoutput + " " + bufferoutput);
        output3 = String(buyoutput + " " + selloutput);

    }
    document.getElementById("rawDataOutput_DATE").innerHTML = dateoutput; //JSON.stringify(output,null,4);
	document.getElementById("rawDataOutput_OUTPUT1").innerHTML = output1;
	document.getElementById("rawDataOutput_OUTPUT2").innerHTML = output2;
	document.getElementById("rawDataOutput_OUTPUT3").innerHTML = output3;

    // Om man vill göra ett flöde med alla timestamps, funkar ej dock.
  /*  div = document.getElementById('rawdataoutputdiv');
    div.insertAdjacentHTML('afterbegin', '<div>' + dateoutput + '<hr></div>');
    div.insertAdjacentHTML('afterbegin', '<div>' + output1 + '<hr></div>');
    div.insertAdjacentHTML('afterbegin', '<div>' + output2 + '<hr></div>');
    div.insertAdjacentHTML('afterbegin', '<div>' + output3 + '<hr></div>');*/
}



function updateUserGauges(simulatorData) {

// Max Value of gauges
var maxValue =  20.0;
var maxValueWindSpeed = 6.0;
var maxValueNetProduction = 3.0;
var MaxValueBuffer = 15.0;

// First epoch
 if (simulatorData  == null){
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
 }else {
    // First Value is a string showing the formatted value. Used for the string showing the value.
    // Second Value is a string showing the percentage of the total value that the current value is. Used for the gauge.
    consumption = simulatorData.consumption.substring(0,5);
    consumptionoutput = String((consumption/ maxValue)*100.0 );

    production = simulatorData.production.substring(0,5);
    productionoutput = String((production/ maxValue)*100.0 );

    windspeedFactor = 5.0; // Production/Windspeedfactor = Windspeed
    windspeed = String ( parseFloat(simulatorData.production / windspeedFactor)).substring(0,5);
    windspeedoutput = String((windspeed/ maxValueWindSpeed)*100.0 );

    netproduction = String(parseFloat(production)-parseFloat(consumption)).substring(0,4);
    netproductionoutput = String(( Math.abs(netproduction) / maxValueNetProduction)*100.0 ).substring(0,4);

    buffer = simulatorData.buffer.substring(0,5);
    bufferoutput = String((buffer/ MaxValueBuffer)*100.0 );

    currentelectrictyprice = simulatorData.consumption.substring(0,5); // Ladda upp pris ruben.
    currentelectrictypriceoutput = String((consumption/ maxValue)*100.0 );

    document.getElementById("usergauge_consumption").style.width = consumptionoutput+"%";
    document.getElementById("usergauge_consumption_text").innerHTML = String(consumption)+"kWh";

    document.getElementById("usergauge_production").style.width = productionoutput+"%";
    document.getElementById("usergauge_production_text").innerHTML = production+"kWh";

    document.getElementById("usergauge_windspeed").style.width = windspeedoutput+"%";
    document.getElementById("usergauge_windspeed_text").innerHTML = windspeed+"m/s";

    document.getElementById("usergauge_netproduction").style.width = netproductionoutput+"%";
    document.getElementById("usergauge_netproduction_text").innerHTML = netproduction+"kWh";

    document.getElementById("usergauge_buffer").style.width = bufferoutput+"%";
    document.getElementById("usergauge_buffer_text").innerHTML = buffer+"kWh";

    document.getElementById("usergauge_price").style.width = currentelectrictypriceoutput+"%";
    document.getElementById("usergauge_price_text").innerHTML = currentelectrictyprice+"kr";

    // Set color to red if negative.
    if(parseFloat(netproduction) < 0.0){
        document.getElementById("usergauge_netproduction").style.backgroundColor = '#c70000';
    }else{
        document.getElementById("usergauge_netproduction").style.backgroundColor = '#007300' ;
    }

    }

}

// Only Updates once each tick.
function updateUserSliders(simulatorData) {

    var buyRatio = document.getElementById("buyingRatio").value;
    document.getElementById("buyingRatioText").innerHTML = buyRatio;

    var sellRatio = document.getElementById("sellingRatio").value;
    document.getElementById("sellingRatioText").innerHTML = sellRatio;


}

// Only Updates once each tick.
function updateAdminSliders(simulatorData) {
/*
    var price = document.getElementById("currentelectricityprice").value;
    document.getElementById("currentelectricitypriceText").innerHTML = price;

    var prod = document.getElementById("powerplantproduction").value;
    document.getElementById("powerplantproductionText").innerHTML = prod;

    var marketRatio = document.getElementById("marketRatio").value;
    document.getElementById("marketRatioText").innerHTML = marketRatio;
*/
}

function updateAll(updater, chart, startx, starty, delta, bufferSize=10) {
	fetchDataCycle();
	updateGraph(chart, startx, starty, bufferSize=10);

	var simulatorData = simData[simData.length-1];
	updateRawSimulatorDataOutput(simulatorData);
	updateUserGauges(simulatorData);
	updateUserSliders(simulatorData);
	//updateAdminSliders(simulatorData);

	//uploadData("buyRatio",buyRatio);
	updater = setTimeout(updateAll, delta * 1000, updater, chart, startx, starty, delta, bufferSize);
}
