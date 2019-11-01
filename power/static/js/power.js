var powergraph = (function() {

	function prepare(data, name, xAxis, enabled, color) {
		var plotdata = [];
		for (var key in data) {
			var i = data[key];
			if (i[xAxis] != 0)
				plotdata.push({x: i.timestamp * 1000, y: i[xAxis]})
		}

		function sort_plotdata(a,b) {
			return a.x - b.x;
		}
		plotdata.sort(sort_plotdata);
		var series = {
			name: name,
			data: plotdata,
			visible: enabled,
			color:color,
		};
		return series;
	}

	function draw(series, renderTo, header, yTitle, chartType, stacked){
		//highchart initialization
		var chart;
		$(document).ready(function() {
			chart = new Highcharts.Chart({
				chart: {
					renderTo: renderTo,
					type: chartType,
					animation: false,
				},
				credits: false,
				title: {
					text: header
				},
				xAxis: {
					tickPixelInterval: 50,
					endOnTick: true,
					type: 'datetime',
					dateTimeLabelFormats: {
						day: '%e. %b <br> %Y',
						month: '%b <br> %Y',
						year: '%Y'
					}
				},
				yAxis: {
					tickPixelInterval: 30,
					allowDecimals: false,
					endOnTick: false,
					gridLineColor: '#EDEDED',
					title: {
						text: yTitle
					},
					min: 0,
				},
				tooltip: {
					enabled: true,
					formatter: function() {
							return Highcharts.dateFormat('%b %Y', this.x) + ': ' + this.y;
					}
				},
				legend: {
					enabled: true,
					floating: false,
					layout: 'vertical', 
					borderWidth: 0,
					verticalAlign: 'bottom',
				},
				plotOptions: {
					area: {
						lineWidth: 0,
						lineColor: '#000',
						marker: {
							enabled: true,
							fillColor: this.color,
							radius: 2,
							symbol: 'diamond',
						}					
					},
					series: {
						animation: false,
						stacking: stacked,

					}
				},
				series: series,
			});
		});
		return chart;
	}

	return {
		prepare: prepare,
		draw: draw,
	}
})();

series1 = []
series1.push( powergraph.prepare(power_reading_plotdata, 'Egen avlesing', 'kwh', true, "#113954") );
series1.push( powergraph.prepare(power_payment_plotdata, 'Fra regning', 'usage', true, "#9BA9B3") );



series2 = []
series2.push( powergraph.prepare(power_payment_plotdata, 'Daglig kostnad', 'cost', true, "#113954") );
series2.push( powergraph.prepare(power_payment_plotdata, 'Strømpris', 'price', true, "#9BA9B3") );


series3 = []
series3.push( powergraph.prepare(power_total_cost_plotdata, 'Strømforbruk', 'usage', true, "#5E8FB8") );
series3.push( powergraph.prepare(power_total_cost_plotdata, 'Linjeleie bruk', 'cable', true, "#BA4B29") );
series3.push( powergraph.prepare(power_total_cost_plotdata, 'Linjeleie fastbeløp', 'static', true, "#9E9420") );

graph1 = powergraph.draw(series1, 'reading_graph', "Daglig forbruk", "kWt", 'area', false);
graph2 = powergraph.draw(series2, 'payment_graph', "Strømkostnad", "Kr", 'area', false);
graph3 = powergraph.draw(series3, 'payment_graph2', "Månedlige utgifter", "Kr", 'column', true);
