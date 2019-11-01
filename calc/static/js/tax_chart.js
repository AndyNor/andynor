var visitGraphs = (function() {

	function display_graph( series, renderTo, title, stacking ) {
		var chart = new Highcharts.Chart({
			chart: {
				renderTo: renderTo,
				backgroundColor: false,
				animation: false,
				type: 'area',
				zoomType: 'x'
			},
			credits: {
				enabled: false
			},
			legend: {
				enabled: true
			},
			title: {
				text: title
			},
			subtitle: {
				text: ''
			},
			xAxis: {
			},
			yAxis: {
				allowDecimals: false,
				title: {
					text: ''
				},
				min: 0
			},
			tooltip: {
				enabled: true
			},
			plotOptions: {
				area: {
					stacking: stacking,
					allowPointSelect: false,
					animation: false,
					marker: {
						enabled: false,
						symbol: 'diamond',
						states: {
							hover: false
						}
					},
					lineColor: "#000000",
					lineWidth: 1
				}
			},

			series: series
		});
		return chart;
	}

	return {
		draw: display_graph
	};

})();

$(document).ready(function() {
	var tax_chart1 = visitGraphs.draw( tax_chart_data, 'tax_chart1', 'Skatt som funksjon av inntekt (prosent)', 'percent' );
	var tax_chart2 = visitGraphs.draw( tax_chart_data, 'tax_chart2', 'Skatt som funksjon av inntekt (absolutt)', 'stacked');
	tax_chart2.series[0].hide()
});

