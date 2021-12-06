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

function updateText() {
    var simulatorData = simData[simData.length-1];

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

function updateAll(updater, chart, startx, starty, delta, bufferSize=10) {
	fetchDataCycle();
	updateGraph(chart, startx, starty, bufferSize=10);
	updateText();
	uploadData("buyRatio",buyRatio);
	updater = setTimeout(updateAll, delta * 1000, updater, chart, startx, starty, delta, bufferSize);
}



//update();
