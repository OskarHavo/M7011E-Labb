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

	try {
		productionoutput = "Production: " + simulatorData.production.substring(0, 4) + "kWh";
		consumptionoutput = "Consumption: " + simulatorData.consumption.substring(0, 4) + "kWh";
		bufferoutput = "Buffer: " + simulatorData.buffer.substring(0, 4) + "kWh";
		demand = "Customer demand: " + simulatorData.demand.substring(0, 4);

		dateoutput = String(timeoutput);
		output1 = String(productionoutput + " " + consumptionoutput);
		output2 = String(bufferoutput);
		output3 = String(demand);
	}catch(error) {
		dateoutput = "No Data";
		output1 = "";
		output2 = "";
		output3 = "";
		output4 = "";
	}

	//TODO Gör vad du vill med värdena. Just nu ska dom skrivas ut i loggen.
    //document.getElementById("rawDataOutput_DATE").innerHTML = dateoutput; //JSON.stringify(output,null,4);
	//document.getElementById("rawDataOutput_OUTPUT1").innerHTML = output1;
	//document.getElementById("rawDataOutput_OUTPUT2").innerHTML = output2;
	//document.getElementById("rawDataOutput_OUTPUT3").innerHTML = output3;
}

// Only Updates once each tick.
function updateAdminSliders(simulatorData) {

    var price = document.getElementById("currentelectricityprice").value;
    document.getElementById("currentelectricitypriceText").innerHTML = price;

    var prod = document.getElementById("powerplantproduction").value;
    document.getElementById("powerplantproductionText").innerHTML = prod;

    var marketRatio = document.getElementById("marketRatio").value;
    document.getElementById("marketRatioText").innerHTML = marketRatio;

}

function updateAll(updater, delta, bufferSize=10) {
	fetchDataCycle().then(value => {
		//var simulatorData = simData[simData.length - 1];
		updateRawSimulatorDataOutput(value);
		updateAdminSliders(value);

		//uploadData("buyRatio",buyRatio);
		updater = setTimeout(updateAll, delta * 1000, updater, delta, bufferSize);
	});

}