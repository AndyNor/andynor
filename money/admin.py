
from django.contrib import admin
from money import models

admin.site.register(models.Salary)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.Downpayment)
admin.site.register(models.FastUtgift)

@admin.register(models.BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
	list_display = ('amount', 'amount_factor', 'account', 'eier', 'accounting_date', 'description', 'related_transaction', 'unique_reference')
	search_fields = ('description',)
	list_filter = ('eier', 'account',)
	autocomplete_fields = ('related_transaction',)
	ordering = ('-accounting_date',)


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ('name', 'account_type', 'sub_category', 'description', 'owner', 'account_number', 'available', 'balance', 'credit_limit')
	search_fields = ('name', 'account_number', 'description')
	list_filter = ('account_type',)


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('amount', 'account', 'owner', 'date', 'category', 'sub_category', 'comment', 'is_asset',)
	search_fields = ('amount', 'comment',)
	list_filter = ('owner','account', 'is_asset')