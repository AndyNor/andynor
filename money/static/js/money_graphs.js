var SalaryL1Graphs = (function() {

	function stringToTimeStamp( string ) {//YYYY-mm-dd to javascript date
		return new Date( Date.parse( string ) ).getTime();
	}

	function formatMoney(sSymbol, value) {
		vValue = parseFloat( value );
		aDigits = vValue.toFixed(0).split(" ");
		aDigits[0] = aDigits[0].split("").reverse().join("").replace(/(\d{3})(?=\d)/g, "$1 ").split("").reverse().join("");
		return sSymbol + aDigits.join(".");
	}

	function extractDataYear( data ) {
		var loop = [ Array("retirement", "#ba4e4e", "Retirement"), Array("tax", "#dc6c6c", "Tax"), Array("nett", "#9bd569", "Net income") ];
		var series = [];
		for ( j in loop ) {
			var seriesData = [];
			var categories = [];
			for (var i in data) {
				seriesData.push({
					y: data[ i ][ loop[ j ][ 0 ] ],
				});
				categories.push(String(data[ i ].year));
			}
			series.push({
				data: seriesData,
				categories: categories,
				name: loop[ j ][2],
				color: loop[ j ][1],
				tooltip: {
					enabled: false,
				}
			});
		}
		return series;
	}

	function extractDataAccount( data ) {
		//console.log( data );
		var series = [];
		var seriesData = [];
		var categories = [];
		for (var i in data) {
			yValue = data[i].real;
			if (yValue < 0) {
				color = "#dc6c6c"
			}
			else {
				color = "#9bd569"
			}
			seriesData.push({
				name: formatMoney( ' ', data[i].real ),
				y: yValue,
				color: color,
			})
			categories.push( data[i].account );
		}
		series.push({
			data: seriesData,
			categories: categories,
			tooltip: {
				enabled: true,
				formatter: function() {
						return this.point.name;
				}
			}
		})
		//console.log( series )
		return series;
	}

	function display_graph( series, renderTo, title, chartType, yMin, legend, stacked, reversed ) {
		var chart = new Highcharts.Chart({
			chart: {
				renderTo: renderTo,
				backgroundColor: false,
				animation: false,
				type: chartType,
				zoomType: "xy"
			},
			credits: {
				enabled: false,
			},
			legend: {
				enabled: legend,
			},
			title: {
				text: title,
			},
			subtitle: {
				text: ''
			},
			xAxis: {
				reversed: reversed,
				categories: series[0].categories,
			},
			yAxis: {
				allowDecimals: false,
				title: {
					text: ''
				},
				min: yMin,
			},
			tooltip: series[0].tooltip,
			plotOptions: {
				series: {
					animation: false,
					stacking: stacked,
				},
			column: {
				pointPadding: 0.05,
				groupPadding: 0.05,
				borderWidth: 1,
			},
			},
			series: series,
		})
		return chart
	}

	return {
		draw: display_graph,
		extractDataAccount: extractDataAccount,
		extractDataYear: extractDataYear
	}

})();

$(document).ready(function() {
	var balance_data_prepared = SalaryL1Graphs.extractDataAccount( balance_data );
	var graph_balance_data = SalaryL1Graphs.draw( balance_data_prepared, 'graph_per_account', '', 'bar', undefined, false, false, true );

	var year_data_prepared = SalaryL1Graphs.extractDataYear( year_data );
	var graph_year_data = SalaryL1Graphs.draw( year_data_prepared, 'graph_per_year', '', 'column', 0, true, true, true );
})
