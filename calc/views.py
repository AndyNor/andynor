# coding: UTF8

from django.shortcuts import render
#from django.http import HttpResponseRedirect  # redirect after successfull POST
from django.template import RequestContext  # required for csrf
#from django.contrib import messages  # Message system
import json  # used for json export
import math


APP_NAME = 'app_calc'
# Generic object to store data


class Object(object):
	pass


def readPost(attr, default, request):
	return float(request.POST.get(attr, default).replace(' ', '').replace(',', '.'))


def index(request):
	return render(request, 'calc.html', {
	})


def loan(request):

	user_var = Object()
	user_var.laanebehov = readPost('laanebehov', '125000', request)
	user_var.termingebyr = readPost('termingebyr', '85', request)
	user_var.nomrente = readPost('nomrente', '5.1', request)
	user_var.tinglysning = readPost('tinglysning', '1300', request)
	user_var.terminer = readPost('terminer', '12', request)
	user_var.etablering = readPost('etablering', '2690', request)
	user_var.loepetid = readPost('loepetid', '5', request)

	faktisk_lanebehov = user_var.laanebehov + user_var.tinglysning + user_var.etablering
	terminrente = (user_var.nomrente / user_var.terminer) / 100
	antall_terminer = user_var.terminer * user_var.loepetid
	optimize_constant = math.pow((1 + terminrente), antall_terminer)
	annuitetsfaktor = terminrente * optimize_constant / (optimize_constant - 1)
	innbetaling_per_termin = faktisk_lanebehov * (terminrente / (1 - math.pow((1 + terminrente), -antall_terminer))) + user_var.termingebyr
	totalkostnad = antall_terminer * innbetaling_per_termin
	kostnad_renter_gebyrer = totalkostnad - user_var.laanebehov
	serie_avdrag = faktisk_lanebehov / antall_terminer

	serie_totalkostnad = 0
	serie_temp_restlan = faktisk_lanebehov
	for i in range(0, int(antall_terminer)):
		serie_totalkostnad += serie_avdrag + user_var.termingebyr + (serie_temp_restlan * terminrente)
		serie_temp_restlan -= serie_avdrag

	serie_kostnad_renter_gebyrer = serie_totalkostnad - user_var.laanebehov

	serie_plan = []
	annuitet_plan = []
	restlaan = faktisk_lanebehov
	serie_restlan = faktisk_lanebehov
	for i in range(0, int(antall_terminer)):
		annuitet = annuitetsfaktor * faktisk_lanebehov + user_var.termingebyr
		rente = (restlaan * terminrente) + user_var.termingebyr
		serie_rente = serie_restlan * terminrente + user_var.termingebyr
		avdrag = annuitet - rente
		termin_belop = avdrag + rente
		restlaan -= avdrag
		serie_restlan -= serie_avdrag
		serie_termin_belop = serie_avdrag + serie_rente

		serie_plan.append((i + 1, int(rente), int(avdrag), int(termin_belop), int(restlaan)))
		annuitet_plan.append((i + 1, int(serie_rente), int(serie_avdrag), int(serie_termin_belop), int(serie_restlan)))

	table_head = ('Termin', 'Renter + gebyr', 'Avdrag', 'Terminbeløp', 'Restgjeld')

	serie = {
		'per_termin': int(innbetaling_per_termin),
		'total_kost': int(totalkostnad),
		'rebyr_renter': int(kostnad_renter_gebyrer),
		'plan': serie_plan,
	}

	annuitet = {
		'per_termin': 'Variabel',
		'total_kost': int(serie_totalkostnad),
		'rebyr_renter': int(serie_kostnad_renter_gebyrer),
		'plan': annuitet_plan,
	}

	return render(request, 'calc_loan.html', {
		'user_var': user_var,
		'serie': serie,
		'annuitet': annuitet,
		'table_head': table_head,
	})


def tax(request, year=2016):
	""" Norwegian tax calculator """

	year = int(year)

	if year == 2016:
		constant = Object()							#
		constant.VERSION = 2016						#
		constant.innkrevingsgrense = 100 			#
		constant.klassefradrag = 51750 				#
		constant.minstefradrag = 0.43				#
		constant.minstefradrag_min = 4000			#
		constant.minstefradrag_max = 91450			#
		constant.fagforeningssats = 0.011
		constant.fagforeningssats_max = 3850		#
		constant.pensjonstrekk = 0.0				#
		constant.formue_frigrense = 1400000 		#
		constant.formueskatt_kommune = 0.007		#
		constant.formueskatt_stat = 0.0015			#
		constant.bsu_frigrense = 0.2 				#
		constant.bsu_frigrense_max = 4000 			#
		constant.skatt = 0.25 						#
		constant.avgift_trygd = 0.082				#
		constant.avgift_trygd_innslag = 49650		#
		constant.avgift_trygd_max = 0.25			#
		constant.toppskatt_trinn01 = 0.0044 			#
		constant.toppskatt_trinn01_innslag = 159800 	#
		constant.toppskatt_trinn02 = 0.017 				#
		constant.toppskatt_trinn02_innslag = 224900 	#
		constant.toppskatt_trinn1 = 0.107 			#
		constant.toppskatt_trinn1_innslag = 565400 	#
		constant.toppskatt_trinn2 = 0.137 			#
		constant.toppskatt_trinn2_innslag = 909500 	#
		constant.aksje_skjermingsfradrag = 0.03
		constant.frivillig_maks = 12000

	if year == 2013:
		constant = Object()
		constant.VERSION = 2013
		constant.innkrevingsgrense = 100
		constant.klassefradrag = 47150
		constant.minstefradrag = 0.40
		constant.minstefradrag_min = 4000
		constant.minstefradrag_max = 81300
		constant.fagforeningssats = 0.011
		constant.fagforeningssats_max = 3850
		constant.pensjonstrekk = 0.02
		constant.formue_frigrense = 870000
		constant.formueskatt_kommune = 0.007
		constant.formueskatt_stat = 0.004
		constant.bsu_frigrense = 0.2
		constant.bsu_frigrense_max = 4000
		constant.skatt = 0.28
		constant.avgift_trygd = 0.078
		constant.avgift_trygd_innslag = 39600
		constant.avgift_trygd_max = 0.25
		constant.toppskatt_trinn1 = 0.09
		constant.toppskatt_trinn1_innslag = 509600
		constant.toppskatt_trinn2 = 0.12
		constant.toppskatt_trinn2_innslag = 828300
		constant.aksje_skjermingsfradrag = 0.03
		constant.frivillig_maks = 12000

	if year == 2012:
		constant = Object()
		constant.VERSION = 2012
		constant.innkrevingsgrense = 100
		constant.klassefradrag = 45350
		constant.minstefradrag = 0.38
		constant.minstefradrag_min = 4000
		constant.minstefradrag_max = 78150
		constant.fagforeningssats = 0.011
		constant.fagforeningssats_max = 3750
		constant.pensjonstrekk = 0.02
		constant.formue_frigrense = 750000
		constant.formueskatt_kommune = 0.007
		constant.formueskatt_stat = 0.004
		constant.bsu_frigrense = 0.2
		constant.bsu_frigrense_max = 4000
		constant.skatt = 0.28
		constant.avgift_trygd = 0.078
		constant.avgift_trygd_innslag = 39600
		constant.avgift_trygd_max = 0.25
		constant.toppskatt_trinn1 = 0.09
		constant.toppskatt_trinn1_innslag = 490000
		constant.toppskatt_trinn2 = 0.12
		constant.toppskatt_trinn2_innslag = 796400
		constant.aksje_skjermingsfradrag = 0.03
		constant.frivillig_maks = 12000

	if year == 2011:
		constant = Object()
		constant.VERSION = 2011
		constant.innkrevingsgrense = 100
		constant.klassefradrag = 42210
		constant.minstefradrag = 0.38
		constant.minstefradrag_min = 31800
		constant.minstefradrag_max = 78150
		constant.fagforeningssats = 0.011
		constant.fagforeningssats_max = 3750
		constant.pensjonstrekk = 0.02
		constant.formue_frigrense = 750000
		constant.formueskatt_kommune = 0.007
		constant.formueskatt_stat = 0.004
		constant.bsu_frigrense = 0.2
		constant.bsu_frigrense_max = 4000
		constant.skatt = 0.28
		constant.avgift_trygd = 0.078
		constant.avgift_trygd_innslag = 39600
		constant.avgift_trygd_max = 0.25
		constant.toppskatt_trinn1 = 0.09
		constant.toppskatt_trinn1_innslag = 471200
		constant.toppskatt_trinn2 = 0.12
		constant.toppskatt_trinn2_innslag = 765800
		constant.aksje_skjermingsfradrag = 0.03
		constant.frivillig_maks = 12000

	user_var = Object()
	user_var.arbeidsinntekter = readPost('arbeidsinntekter', '450000', request)
	user_var.renteinntekter = readPost('renteinntekter', '0', request)
	user_var.renteutgifter = readPost('renteutgifter', '0', request)
	user_var.utleie_overskudd = readPost('utleie_overskudd', '0', request)
	user_var.aksjeutbytte = readPost('aksjeutbytte', '0', request)
	user_var.bsu_sparing = readPost('bsu_sparing', '0', request)
	user_var.formue = readPost('formue', '0', request)
	user_var.gjeld = readPost('gjeld', '0', request)
	user_var.frivillig = readPost('frivillig', '0', request)
	user_var.fagforening = readPost('fagforening', '0', request)
	user_var.pensjon = readPost('pensjon', '0', request)

	def limit(amount, pct, max, min=0.0):
		value = amount * pct
		if value > max:
			return max
		if value < min:
			return min
		return value

	def positive(num):
		if num < 0.0:
			return 0.0
		else:
			return num

	def calc_tax(constant, user_var):
		result = Object()
		#sanity checks
		if user_var.arbeidsinntekter < 0.0:
			user_var.arbeidsinntekter = 0.0

		#skatter
		if user_var.arbeidsinntekter <= constant.avgift_trygd_innslag:
			result.trygdeskatt = 0.0
		else:
			result.trygdeskatt = user_var.arbeidsinntekter * constant.avgift_trygd
			steplimit = (user_var.arbeidsinntekter - constant.avgift_trygd_innslag) * constant.avgift_trygd_max
			if result.trygdeskatt > steplimit:
				result.trygdeskatt = steplimit

		#fradrag
		result.minstefradrag = limit(user_var.arbeidsinntekter, constant.minstefradrag, constant.minstefradrag_max, constant.minstefradrag_min)
		if user_var.fagforening == 0.0:
			result.fagforening_fradrag = limit(user_var.arbeidsinntekter, constant.fagforeningssats, constant.fagforeningssats_max)
		else:
			result.fagforening_fradrag = limit(user_var.fagforening, 1.0, constant.fagforeningssats_max)

		if user_var.pensjon == 0.0:
			result.pensjon_fradrag = user_var.arbeidsinntekter * constant.pensjonstrekk
		else:
			result.pensjon_fradrag = user_var.pensjon
		result.rentefradrag = user_var.renteutgifter
		result.frivillig_fradrag = limit(user_var.frivillig, 1.0, constant.frivillig_maks)

		result.totale_fradrag = result.minstefradrag + result.fagforening_fradrag + result.pensjon_fradrag + result.rentefradrag + constant.klassefradrag + result.frivillig_fradrag

		#beregning av skatter på inntekt
		result.kapitalinntekter = user_var.renteinntekter + user_var.utleie_overskudd + (user_var.aksjeutbytte * (1.0 - constant.aksje_skjermingsfradrag))
		skattemessig_arbeidsinntekt = user_var.arbeidsinntekter + result.kapitalinntekter - result.totale_fradrag
		result.arbeidsinntektskatt = positive(skattemessig_arbeidsinntekt * constant.skatt)

		#toppskatt
		result.toppskatt_trinn2 = positive((user_var.arbeidsinntekter - constant.toppskatt_trinn2_innslag) * constant.toppskatt_trinn2)
		tt1_grunnlag = limit(user_var.arbeidsinntekter, 1, constant.toppskatt_trinn2_innslag)
		result.toppskatt_trinn1 = positive((tt1_grunnlag - constant.toppskatt_trinn1_innslag) * constant.toppskatt_trinn1)

		try:
			tt02_grunnlag = limit(user_var.arbeidsinntekter, 1, constant.toppskatt_trinn1_innslag)
			result.toppskatt_trinn02 = positive((tt02_grunnlag - constant.toppskatt_trinn02_innslag) * constant.toppskatt_trinn02)
		except:
			result.toppskatt_trinn02 = 0.0
			constant.toppskatt_trinn02 = 0.0

		try:
			tt01_grunnlag = limit(user_var.arbeidsinntekter, 1, constant.toppskatt_trinn02_innslag)
			result.toppskatt_trinn01 = positive((tt01_grunnlag - constant.toppskatt_trinn01_innslag) * constant.toppskatt_trinn01)
		except:
			result.toppskatt_trinn01 = 0.0
			constant.toppskatt_trinn01 = 0.0

		#formue
		formue_skattbar = positive(user_var.formue - user_var.gjeld - constant.formue_frigrense)
		skatt_formue_stat = formue_skattbar * constant.formueskatt_stat
		skatt_formue_kommune = formue_skattbar * constant.formueskatt_kommune
		result.formueskatt = skatt_formue_stat + skatt_formue_kommune

		result.bsu_fradrag = limit(user_var.bsu_sparing, constant.bsu_frigrense, constant.bsu_frigrense_max)
		#summer endelig skatt
		result.total_skatt = positive(result.trygdeskatt + result.arbeidsinntektskatt + result.toppskatt_trinn1 + result.toppskatt_trinn2 + result.toppskatt_trinn01 + result.toppskatt_trinn02 + result.formueskatt - result.bsu_fradrag)
		result.delvis_skatt = positive(result.trygdeskatt + result.arbeidsinntektskatt + result.toppskatt_trinn1 + result.toppskatt_trinn2 + result.toppskatt_trinn01 + result.toppskatt_trinn02)
		result.netto = user_var.arbeidsinntekter + user_var.renteinntekter + user_var.utleie_overskudd + user_var.aksjeutbytte - result.delvis_skatt
		try:
			result.total_skatt_prosent = result.total_skatt / (user_var.arbeidsinntekter + result.kapitalinntekter)
		except:
			result.total_skatt_prosent = 0.0
		result.justert_skatt = result.total_skatt_prosent * (12 / 10.5)

		return result

	# data for the current page
	result = calc_tax(constant, user_var)

	# data for the chart
	series_arbeidsinntektskatt = []
	series_trygdeskatt = []
	series_toppskatt_trinn1 = []
	series_toppskatt_trinn2 = []
	series_toppskatt_trinn01 = []
	series_toppskatt_trinn02 = []
	series_netto = []
	salary = 0.0
	max_salary = 1200000.0
	user_var.arbeidsinntekter_tmp = user_var.arbeidsinntekter
	while salary < max_salary:
		user_var.arbeidsinntekter = salary
		instance = calc_tax(constant, user_var)
		series_arbeidsinntektskatt.append({'x': int(salary), 'y': int(instance.arbeidsinntektskatt)})
		series_trygdeskatt.append({'x': int(salary), 'y': int(instance.trygdeskatt)})
		series_toppskatt_trinn1.append({'x': int(salary), 'y': int(instance.toppskatt_trinn1)})
		series_toppskatt_trinn2.append({'x': int(salary), 'y': int(instance.toppskatt_trinn2)})
		series_toppskatt_trinn01.append({'x': int(salary), 'y': int(instance.toppskatt_trinn01)})
		series_toppskatt_trinn02.append({'x': int(salary), 'y': int(instance.toppskatt_trinn02)})
		series_netto.append({'x': int(salary), 'y': int(instance.netto)})

		salary = (salary + 1000) * 1.08

	chart_series = [
		{'name': 'Netto inntekt', 'color': '#B1DEFA', 'data': series_netto},
		{'name': 'Toppskatt nivå 2', 'color': '#0D400B', 'data': series_toppskatt_trinn2},
		{'name': 'Toppskatt nivå 1', 'color': '#2A8A27', 'data': series_toppskatt_trinn1},
		{'name': 'Trinnskatt nivå 2', 'color': '#2A8A17', 'data': series_toppskatt_trinn02},
		{'name': 'Trinnskatt nivå 1', 'color': '#2A8A07', 'data': series_toppskatt_trinn01},
		{'name': 'Inntektskatt', 'color': '#7AE876', 'data': series_arbeidsinntektskatt},
		{'name': 'Trygdeskatt', 'color': '#B51616', 'data': series_trygdeskatt},
	]
	user_var.arbeidsinntekter = user_var.arbeidsinntekter_tmp  # reset after loop

	return render(request, 'calc_tax.html', {
		'kapitalinntekter': result.kapitalinntekter,
		'arbeidsinntektskatt': result.arbeidsinntektskatt,
		'trygdeskatt': result.trygdeskatt,
		'minstefradrag': result.minstefradrag,
		'frivillig_fradrag': result.frivillig_fradrag,
		'fagforening_fradrag': result.fagforening_fradrag,
		'pensjon_fradrag': result.pensjon_fradrag,
		'rentefradrag': result.rentefradrag,
		'bsu_fradrag': result.bsu_fradrag,
		'formueskatt': result.formueskatt,
		'toppskatt_trinn01': result.toppskatt_trinn01,
		'toppskatt_trinn02': result.toppskatt_trinn02,
		'toppskatt_trinn1': result.toppskatt_trinn1,
		'toppskatt_trinn2': result.toppskatt_trinn2,
		'totale_fradrag': result.totale_fradrag,
		'total_skatt': result.total_skatt,
		'total_skatt_prosent': result.total_skatt_prosent,
		'justert_skatt': result.justert_skatt,
		'constant': constant,
		'user_var': user_var,
		'tax_data_json': json.dumps(chart_series),
	})
