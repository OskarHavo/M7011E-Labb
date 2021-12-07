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


// Only Updates once each tick.
function updateAdminSliders(simulatorData) {

    var price = document.getElementById("currentelectricityprice").value;
    document.getElementById("currentelectricitypriceText").innerHTML = price;

    var prod = document.getElementById("powerplantproduction").value;
    document.getElementById("powerplantproductionText").innerHTML = prod;

    var marketRatio = document.getElementById("marketRatio").value;
    document.getElementById("marketRatioText").innerHTML = marketRatio;

}

function updateAll(updater, chart, startx, starty, delta, bufferSize=10) {
	fetchDataCycle();

	var simulatorData = simData[simData.length-1];
	updateAdminSliders(simulatorData);

	//uploadData("buyRatio",buyRatio);
	updater = setTimeout(updateAll, delta * 1000, updater, chart, startx, starty, delta, bufferSize);
}