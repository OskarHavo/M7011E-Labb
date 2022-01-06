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

var adminSimData = [];
var trailLength = 2;

function fetchDataCycle() {
	return post('/fetch_admin', {}).then(response => {
		//if (simData.length== 0 || simData[simData.length - 1]["timestamp"] != response["timestamp"]) {
			adminSimData.push(response)
			if (adminSimData.length > trailLength) {
				adminSimData.slice(1, adminSimData.length)
			}
			console.log(adminSimData[adminSimData.length - 1])
		return adminSimData[adminSimData.length-1]
		//}
	});
}

const post = (url, params) => request(url,params,'GET');
const put = (url,params) => request(url,params,"PUT");


function updateRawSimulatorDataOutput(simulatorData) {

	// Set the text in the top bar
	document.getElementById("datetext").innerHTML = simulatorData.timestamp;

}

function updateAdminGauges(simulatorData) {

	// Max Value of gauges
	var maxValue = 30.0;
	var maxProductionValue = 100.0;
	var maxValuePrice = 50.0;
	var MaxValueDemand = 100.0;


	try {
		// First Value is a string showing the formatted value. Used for the string showing the value.
		// Second Value is a string showing the percentage of the total value that the current value is. Used for the gauge.

		production = simulatorData.production.substring(0, 5);
		productionoutput = String((production / maxProductionValue) * 100.0);

		productionstatus = simulatorData.running.substring(0, 3);

		marketdemand = simulatorData.demand.substring(0, 5);
		marketdemandoutput = String((marketdemand / MaxValueDemand) * 100.0);

		modelledelectrictyprice = simulatorData.modeledPrice.substring(0, 5);
		modelledelectrictypriceoutput = String((modelledelectrictyprice / maxValuePrice) * 100.0);

		document.getElementById("admingauge_production").style.width = productionoutput + "%";
		document.getElementById("admingauge_production_text").innerHTML = production + "kWh";



		document.getElementById("admingauge_marketdemand").style.width = marketdemandoutput + "%";
		document.getElementById("admingauge_marketdemand_text").innerHTML = marketdemand + "%";

		document.getElementById("admingauge_modelledprice").style.width = modelledelectrictypriceoutput + "%";
		document.getElementById("admingauge_modelledprice_text").innerHTML = modelledelectrictyprice + "kr";

		// Set color to red if stopped. Yellow if starting. Green if Running.
		if (parseInt(productionstatus) == 0) {
			document.getElementById("admingauge_productionstatus_text").style.color = '#c70000';
			productionstatusoutput = "Stopped";
		} else if(parseInt(productionstatus) == 10) {
			document.getElementById("admingauge_productionstatus_text").style.color = '#007300';
			productionstatusoutput = "Running";
		}else{
		    document.getElementById("admingauge_productionstatus_text").style.color = '#FFD400';
			productionstatusoutput = "Starting";
		}


		 document.getElementById("admingauge_productionstatus_text").innerHTML = productionstatusoutput;

	} catch(error) {
	    console.log(error);
		production = "";
		productionoutput = "";

		productionstatus = "";

		marketdemand = "";
		marketdemandoutput = "";

		modelledelectrictyprice = "";
		modelledelectrictypriceoutput = "";

	}
}

function uploadData(valuename, param) {
	put('/fetch_admin', {"valueName":valuename,"data":param}).then(response => {
	});
}


// Only Updates once each tick.
function updateAdminSliders(simulatorData) {

    //var price = document.getElementById("currentelectricityprice").value;
	document.getElementById("currentelectricityprice").value = simulatorData.price;
    document.getElementById("currentelectricitypriceText").innerHTML = simulatorData.price+"kr";

    document.getElementById("powerplantproduction").value = simulatorData.maxCapacityPercentage *simulatorData.maxCapacity;
    document.getElementById("powerplantproductionText").innerHTML = simulatorData.maxCapacityPercentage*100 +"%";

    document.getElementById("marketRatio").value = simulatorData.sellRatio*100;
    document.getElementById("marketRatioText").innerHTML = simulatorData.sellRatio*100+"%";

}


function htmlToTable(){
    	html = "<table><thead><tr><th>Name</th><th>Description</th></tr></thead><tbody><tr><td>Name1</td><td>Description1</td></tr><tr><td>Name2</td><td>Description2</td></tr><tr><td>Name3</td><td>Description3</td></tr></tbody></table>";
		var table = document.getElementById("prosumertableinadmin");
	//	if(typeof table !== 'undefined' && table !== null) {

        table.innerHTML = html;

  	//	}
}

function updateAll(updater, delta, bufferSize=10) {
	fetchDataCycle().then(value => {
		//var simulatorData = simData[simData.length - 1];
		updateRawSimulatorDataOutput(value);
		updateAdminGauges(value);
		updateAdminSliders(value);
		htmlToTable();

		//uploadData("buyRatio",buyRatio);
		updater = setTimeout(updateAll, delta * 1000, updater, delta, bufferSize);
	});

}


document.addEventListener('DOMContentLoaded', (event) => {
		var slider = document.querySelectorAll('.slider');
		slider.item(0).oninput = function () {
				console.log(this.value);
				uploadData(this.id,parseFloat(this.value));
				document.getElementById("currentelectricitypriceText").innerHTML = this.value+"kr";
		};
		slider.item(1).oninput = function () {
				console.log(this.value);
				uploadData(this.id,parseFloat(this.value)/100);
				document.getElementById("powerplantproductionText").innerHTML = this.value+"%";
		};
		slider.item(2).oninput = function () {
				console.log(this.value);
				uploadData(this.id,parseFloat(this.value)/100);
				document.getElementById("marketRatioText").innerHTML = this.value+"%";
		};
});

updateAdminSliders(fetchDataCycle())