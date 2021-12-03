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
		method
	};
	if ( 'GET' === method ) {
		url += '?' + ( new URLSearchParams( params ) ).toString();
	} else {
		options.body = JSON.stringify( params );
	}

	return fetch( url, options ).then( response => response.json() );
};

const post= (url, params) => request(url,params,'GET');
var k = 0
//var repeater;
function update(updater, chart,startx,starty,delta,bufferSize=10) {
	post('/fetch',{}).then(response=>{
		var i = k;
		k = k + 1;
		var data = response["consumption"];
		addData(chart,i,data);
		if (chart.data.labels.length > bufferSize) {
			removeFirst(chart);
		}
		console.log(response)
		var maximum = Math.max.apply(null,chart.data.datasets[0].data);
		chart.options.scales.yAxes = [{ticks: {min: 0, max:maximum}}];
       		startx ++;
	        starty += Math.floor(Math.random() * 10) -4;
		chart.update();
	        updater = setTimeout(update,delta*1000,updater,chart,startx,starty,delta,bufferSize);
	});
	//var response = XMLHTTPRequest();
	//response.open('GET','/fetch');
	//response.send();
	//var message = response.responseText();
	//console.log(message);
      	
}
//update();
