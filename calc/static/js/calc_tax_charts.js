(function () {
	'use strict';

	function salaryTickLabel(x) {
		var v = Number(x);
		if (v >= 1e6) {
			return (v / 1e6).toFixed(1).replace(/\.0$/, '') + ' M';
		}
		if (v >= 1e3) {
			return (v / 1e3).toFixed(0) + ' k';
		}
		return String(v);
	}

	function totalsByX(raw) {
		var totals = {};
		var si, pi, p, y;
		for (si = 0; si < raw.length; si++) {
			for (pi = 0; pi < raw[si].data.length; pi++) {
				p = raw[si].data[pi];
				y = p.y > 0 ? p.y : 0;
				totals[p.x] = (totals[p.x] || 0) + y;
			}
		}
		return totals;
	}

	function areaFill(series) {
		if (series.name === 'Netto inntekt') {
			return 'rgba(232, 244, 252, 0.82)';
		}
		var c = series.color || '#888';
		return c + '99';
	}

	function datasetLineXY(series, yFromPoint) {
		return {
			label: series.name,
			data: series.data.map(function (pt) {
				return { x: pt.x, y: yFromPoint(pt, series) };
			}),
			borderColor: '#000000',
			backgroundColor: areaFill(series),
			borderWidth: 1,
			fill: true,
			tension: 0.15,
			pointRadius: 0,
		};
	}

	function optionsBase(title, yLabel, isPercent) {
		return {
			responsive: true,
			maintainAspectRatio: true,
			aspectRatio: 1.55 / 1.5,
			interaction: { mode: 'index', intersect: false },
			plugins: {
				title: { display: true, text: title },
				legend: {
					position: 'bottom',
					reverse: true,
					labels: { boxWidth: 10, font: { size: 10 } },
				},
				tooltip: {
					callbacks: {
						title: function (items) {
							if (!items.length) {
								return '';
							}
							var x = items[0].parsed.x;
							return 'Inntekt: ' + Math.round(x).toLocaleString('nb-NO') + ' kr';
						},
						label: function (ctx) {
							var v = ctx.parsed.y;
							if (isPercent) {
								return ctx.dataset.label + ': ' + v.toFixed(1) + ' %';
							}
							return ctx.dataset.label + ': ' + Math.round(v).toLocaleString('nb-NO') + ' kr';
						},
					},
				},
			},
			scales: {
				x: {
					type: 'linear',
					title: { display: true, text: 'Ordinær lønn (kr)' },
					ticks: {
						maxTicksLimit: 12,
						callback: function (val) {
							return salaryTickLabel(val);
						},
					},
				},
				y: (function () {
					var y = {
						stacked: true,
						beginAtZero: true,
						title: { display: true, text: yLabel },
					};
					if (isPercent) {
						y.max = 100;
					}
					return y;
				})(),
			},
		};
	}

	document.addEventListener('DOMContentLoaded', function () {
		var el = document.getElementById('tax-chart-data');
		if (!el || typeof Chart === 'undefined') {
			return;
		}
		var raw;
		try {
			raw = JSON.parse(el.textContent);
		} catch (e) {
			return;
		}
		if (!raw || !raw.length || !raw[0].data || !raw[0].data.length) {
			return;
		}

		var totals = totalsByX(raw);
		var pctRaw = raw.map(function (s) {
			return {
				name: s.name,
				color: s.color,
				data: s.data.map(function (pt) {
					var t = totals[pt.x] || 0;
					var y = pt.y > 0 ? pt.y : 0;
					return { x: pt.x, y: t > 0 ? (y / t) * 100 : 0 };
				}),
			};
		});

		/* Bottom of stack first: skatter nederst, netto øverst (Chart.js tegner første datasett nederst) */
		var pctBottomUp = pctRaw.slice().reverse();

		var ctxPct = document.getElementById('tax_chart_percent');
		if (ctxPct) {
			new Chart(ctxPct.getContext('2d'), {
				type: 'line',
				data: {
					datasets: pctBottomUp.map(function (s) {
						return datasetLineXY(s, function (pt) {
							return pt.y;
						});
					}),
				},
				options: optionsBase(
					'Skatt som funksjon av inntekt (prosent)',
					'Andel (%)',
					true
				),
			});
		}

		var absBottomUp = raw.slice(1).reverse();
		var ctxAbs = document.getElementById('tax_chart_abs');
		if (ctxAbs) {
			new Chart(ctxAbs.getContext('2d'), {
				type: 'line',
				data: {
					datasets: absBottomUp.map(function (s) {
						return datasetLineXY(s, function (pt) {
							return pt.y;
						});
					}),
				},
				options: optionsBase(
					'Skatt som funksjon av inntekt (absolutt)',
					'Kr',
					false
				),
			});
		}
	});
})();
