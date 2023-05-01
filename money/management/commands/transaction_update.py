# -*- coding: utf-8 -*-
""" Hensikten med denne koden er å fikse hovedkategori basert på subkategori. De kan være ute av sync dersom knytning mellom disse endres manuelt """
from django.core.management.base import BaseCommand
from money.models import Transaction
from mysite.models import ApplicationLog

class Command(BaseCommand):
	def handle(self, **options):

		checked = 0
		subcat_changed = 0
		is_consumption_changed = 0

		for t in Transaction.objects.all():
			checked += 1

			if not(t.category.pk == t.sub_category.parent_category.pk):
				t.category = t.sub_category.parent_category
				t.save()
				subcat_changed += 1
				print(f"Rettet {t} til kategori = {t.sub_category.parent_category}")

			if not(t.is_consumption == t.sub_category.is_consumption):
				t.is_consumption = t.sub_category.is_consumption
				t.save()
				is_consumption_changed += 1
				print(f"Rettet {t} til forbruk = {t.sub_category.is_consumption}")


		logg_entry_message = f"Sjekket {checked} transaksjoner. {subcat_changed} subkategorier ble rettet. {is_consumption_changed} forbruk ble rettet."
		print(logg_entry_message)
		logg_entry = ApplicationLog.objects.create(
				event_type="Money update",
				message=logg_entry_message,
		)

