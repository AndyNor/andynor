# -*- coding: utf-8 -*-
"""
Hensikten med denne koden er å fikse tilknytning virksomhet for DRIFT-brukere
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from money.models import BankTransaction, Account
from mysite.models import ApplicationLog
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib.auth.models import User
from hashlib import sha256
import urllib.parse
import requests
import os
import time
import datetime

class Command(BaseCommand):
	def handle(self, **options):

		runtime_t0 = time.time()

		HARDCODED_OWNER = User.objects.get(pk=1)  # hardcoded to my own user

		CUSTOMERID = HARDCODED_OWNER.profile.BANK_CUSTOMERID
		CLIENTID = HARDCODED_OWNER.profile.BANK_CLIENTID
		SECRET = HARDCODED_OWNER.profile.BANK_SECRET

		LOG_EVENT_TYPE = "SBanken API"
		log_message = ""

		def create_authenticated_http_session(client_id, client_secret):
			try:
				print("Kobler opp med clientID %s*** og secret %s***" % (CLIENTID[0:2], SECRET[0:2]))
				oauth2_client = BackendApplicationClient(client_id=urllib.parse.quote(client_id))
				session = OAuth2Session(client=oauth2_client)
				session.fetch_token(
					token_url='https://auth.sbanken.no/identityserver/connect/token',
					client_id=urllib.parse.quote(client_id),
					client_secret=urllib.parse.quote(client_secret)
				)
				return session
			except Exception as e:
				print("Klarte ikke koble til med oppgitte autentiseringsparametre")
				print("Error: %s" % e)
				logg_entry = ApplicationLog.objects.create(
					event_type=LOG_EVENT_TYPE,
					message=("Kunne ikke koble til: %s" % e),
				)



		def sbanken_get(http_session, url, headers):
			if http_session:
				response = http_session.get(url, headers=headers)
				return response.json()

			else:
				print("Ingen tilkobling, avbryter..")
				return None


		def sbanken_accounts(http_session):
			#https://api.sbanken.no/exec.bank/swagger/index.html?urls.primaryName=Accounts%20v1
			url = "https://publicapi.sbanken.no/apibeta/api/v2/Accounts"
			headers = {'customerId': CUSTOMERID}
			accounts = sbanken_get(http_session, url, headers)
			return accounts


		def sbanken_transactions(http_session, accountID):
			#https://api.sbanken.no/exec.bank/swagger/index.html?urls.primaryName=Transactions%20v1
			url = "https://publicapi.sbanken.no/apibeta/api/v2/Transactions/" + accountID + "/?length=200" #?startDate=2019-12-15&endDate=2019-12-25"
			#1000 is maximum
			headers = {
				'customerId': CUSTOMERID,
				#'length': NUM_ASK_FOR_TRANSACTIONS,
				}
			transactions = sbanken_get(http_session, url, headers)
			return transactions


		### LOGIC ###
		# First we remove all previous transactions that has not been manually verified
		@transaction.atomic()
		def cleanup():
			bt = BankTransaction.objects.filter(related_transaction=None)  # all transactions without connection
			for t in bt:
				t.delete()
		cleanup()

		# We need to update the status (balance) on all the accounts
		http_session = create_authenticated_http_session(CLIENTID, SECRET)
		accounts = sbanken_accounts(http_session)
		if accounts == None:
			return
		for a in accounts['items']:
			try:
				internal_account = Account.objects.get(account_id=a['accountId'])
				internal_account.account_number = a['accountNumber']
				internal_account.available = a['available']
				internal_account.balance = a['balance']
				internal_account.credit_limit = a['creditLimit']
				internal_account.save()
			except:
				message = "Kunne ikke finne intern konto %s (%s). " % (a['name'], a['accountNumber'])
				print(message)
				log_message += message
				continue  # go to next account

			# lets add the new transactions. Sbanken API does not have a unique reference for each transaction. Therefore we make one.
			transactions = sbanken_transactions(http_session, a['accountId'])
			counter_successful = 0
			counter_skipped = 0
			all_hashes = [] # for identification of duplicates

			for t in transactions['items']:
				accounting_date = t['accountingDate']
				accounting_date = datetime.datetime.strptime(accounting_date[0:10], "%Y-%m-%d").date()
				amount = t['amount']
				reservation = bool(t['isReservation'])
				source = t['source']
				description = "%s" % (t['text'])
				unique_text = "%s%s%s" % (accounting_date, amount, description)
				unique_reference = sha256(unique_text.encode('utf-8')).hexdigest()
				all_hashes.append(unique_reference)

				if not BankTransaction.objects.filter(accounting_date=accounting_date, amount=amount, description=description).exists():
					BankTransaction.objects.create(
							eier=HARDCODED_OWNER, # hardcoded to "andre"
							account=internal_account,
							accounting_date=accounting_date,
							isReservation=reservation,
							source=source,
							amount=amount,
							description=description,
							related_transaction=None,
							unique_reference=unique_reference,
						)
					counter_successful += 1
				else:
					counter_skipped += 1
					pass # It is already in the database
			# Done checking all the transactions returned

			# for all duplicates, modify transactions "amount_factor"
			dupes = {i:all_hashes.count(i) for i in all_hashes}
			#print(dupes)
			for hash_value in dupes:
				if dupes[hash_value] > 1:
					try:
						bt = BankTransaction.objects.get(unique_reference=hash_value)
						bt.amount_factor = dupes[hash_value]
						bt.save()
						#print("change %s to %s" % (hash_value, dupes[hash_value]))
					except:
						pass


			message = "%s: Fant %s nye transaksjoner. %s eksisterte fra før. " % (a['name'], counter_successful, counter_skipped)
			print(message)
			log_message += message


		runtime_t1 = time.time()
		logg_total_runtime = runtime_t1 - runtime_t0
		logg_entry_message = "Kjøretid: %s sekunder. %s" % (
				round(logg_total_runtime, 1),
				log_message,
		)
		logg_entry = ApplicationLog.objects.create(
				event_type=LOG_EVENT_TYPE,
				message=logg_entry_message,
		)

