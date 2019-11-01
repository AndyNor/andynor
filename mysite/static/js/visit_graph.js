var visitGraphs = (function() {

	function stringToTimeStamp( string ) {//YYYY-mm-dd to javascript date
		ts = new Date( Date.parse( string ) ).getTime();
		//document.write(" - " + ts)
		return ts
	}



	function extractData( data ) {
		//console.log( data );
		var series = [];
		var seriesData = [];
		for (var i in data) {
			var year = String(data[i].year);
			var month = String(data[i].month);
			if (month.length == 1){
				month = "0" + month;
			}
			var day = data[i].day == undefined ? '01' : String(data[i].day);
			if (day.length == 1){
				day = "0" + day;
			}
			var yyyymmdd = ( year +'-'+ month +'-'+ day );

			seriesData.push({
				x: stringToTimeStamp( yyyymmdd ),
				y: data[i].count,
				name: yyyymmdd,
			})
		}
		series.push({
			data: seriesData
		})
		//console.log( series )
		return series;
	}

	function display_graph( series, renderTo, title ) {
		var chart = new Highcharts.Chart({
			chart: {
				renderTo: renderTo,
				backgroundColor: false,
				animation: false,
				type: 'column',
			},
			credits: {
				enabled: false,
			},
			legend: {
				enabled: false,
			},
			title: {
				text: title,
			},
			subtitle: {
				text: ''
			},
			xAxis: {
				type: 'datetime',
				dateTimeLabelFormats: {
					month: '%d.%b<br>%Y',
				},
			},
			yAxis: {
				allowDecimals: false,
				title: {
					text: 'Counts'
				},
				min: 0,
			},
			tooltip: {
				enabled: true,
				formatter: function() {
						return this.point.name;
				}
			},
			plotOptions: {
				series: {
					animation: false
				}
			},
			series: series,
		})
		return chart
	}

	return {
		draw: display_graph,
		calculate: extractData,
	}

})();

$(document).ready(function() {
	var graph_monthly_data = visitGraphs.calculate( visits_monthly );
	var graph_daily_data = visitGraphs.calculate( visits_daily );
	var graph_monthly = visitGraphs.draw( graph_monthly_data, 'visits_monthly', 'monthly' );
	var graph_daily = visitGraphs.draw( graph_daily_data, 'visits_daily', 'last 30 days' );
})

