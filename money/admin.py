
from django.contrib import admin
from money import models

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'id', 'owner', 'text_color', 'description')
	list_filter = ('owner',)
	search_fields = ('name', 'description', 'owner__username', 'owner__email')
	list_select_related = ('owner',)
	ordering = ('name',)


@admin.register(models.SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'id', 'parent_category', 'owner', 'is_consumption', 'description')
	list_filter = ('owner', 'is_consumption', 'parent_category')
	search_fields = ('name', 'description', 'parent_category__name', 'owner__username', 'owner__email')
	autocomplete_fields = ('parent_category',)
	list_select_related = ('owner', 'parent_category')
	ordering = ('name',)


@admin.register(models.FastUtgift)
class FastUtgiftAdmin(admin.ModelAdmin):
	list_display = ('eier', 'id', 'sub_category', 'dag', 'kostnad', 'comment')
	list_filter = ('eier', 'sub_category', 'dag')
	search_fields = ('comment', 'sub_category__name', 'eier__username', 'eier__email')
	autocomplete_fields = ('sub_category',)
	list_select_related = ('eier', 'sub_category')
	ordering = ('dag',)


@admin.register(models.Downpayment)
class DownpaymentAdmin(admin.ModelAdmin):
	list_display = (
		'owner',
		'id',
		'date',
		'source_account',
		'destination_account',
		'interest_and_fees',
		'repayment',
		'comment',
	)
	list_filter = ('owner', 'date', 'source_account', 'destination_account')
	search_fields = ('comment', 'owner__username', 'owner__email')
	autocomplete_fields = (
		'source_account',
		'destination_account',
		'source_transaction',
		'destination_transaction',
	)
	list_select_related = ('owner', 'source_account', 'destination_account', 'source_transaction', 'destination_transaction')
	date_hierarchy = 'date'
	ordering = ('-date',)

@admin.register(models.BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
	list_display = ('amount', 'id', 'amount_factor', 'account', 'eier', 'accounting_date', 'description', 'related_transaction', 'unique_reference')
	search_fields = ('description', 'source', 'unique_reference', 'account__name', 'eier__username', 'eier__email')
	list_filter = ('eier', 'account', 'hidden', 'isReservation')
	autocomplete_fields = ('related_transaction',)
	ordering = ('-accounting_date',)
	date_hierarchy = 'accounting_date'
	list_select_related = ('account', 'eier', 'related_transaction')


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
	list_display = ('name', 'id', 'account_type', 'sub_category', 'description', 'owner', 'account_number', 'available', 'balance', 'credit_limit')
	search_fields = ('name', 'account_number', 'account_id', 'description', 'sub_category__name', 'owner__username', 'owner__email')
	list_filter = ('account_type', 'owner', 'visible')
	autocomplete_fields = ('sub_category',)
	list_select_related = ('owner', 'sub_category')
	ordering = ('name',)


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('owner', 'id', 'account', 'amount', 'date', 'sub_category', 'comment', 'is_asset',)
	search_fields = ('comment', 'account__name', 'sub_category__name', 'owner__username', 'owner__email')
	list_filter = ('owner', 'account', 'is_asset', 'is_consumption', 'date', 'sub_category', 'category')
	autocomplete_fields = ('account', 'sub_category', 'category')
	list_select_related = ('owner', 'account', 'sub_category', 'category')
	date_hierarchy = 'date'
	ordering = ('-date',)


@admin.register(models.Salary)
class SalaryAdmin(admin.ModelAdmin):
	list_display = ('owner', 'id', 'account', 'date', 'salary', 'extra_hours', 'tax', 'comment')
	search_fields = ('comment', 'owner__username', 'owner__email', 'account__name')
	list_filter = ('owner', 'account', 'date')
	autocomplete_fields = ('transaction', 'account')
	list_select_related = ('owner', 'account', 'transaction')
	date_hierarchy = 'date'
	ordering = ('-date',)
