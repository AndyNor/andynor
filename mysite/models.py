from django import forms
from django.db import models
from django.contrib.auth.models import User
from datetime import date


class ApplicationLog(models.Model):
	opprettet = models.DateTimeField(
			verbose_name="Opprettet",
			auto_now_add=True,
			null=True,
			)
	sist_oppdatert = models.DateTimeField(
			verbose_name="Sist oppdatert",
			auto_now=True,
			)
	event_type = models.CharField(
			verbose_name="event_type",
			max_length=30,
			blank=False, null=False,
			help_text=u"event_type",
			)
	message = models.TextField(
			verbose_name="message",
			blank=False, null=False,
			help_text=u"message",
			)
	def __str__(self):
		return u'%s %s %s' % (self.opprettet.strftime('%Y-%m-%d %H:%M:%S'), self.event_type, self.message)

	class Meta:
		verbose_name_plural = "Applikasjonslogger"
		default_permissions = ('add', 'change', 'delete', 'view')


class SiteLog(models.Model):
	ip = models.GenericIPAddressField()
	priority = models.IntegerField(blank=True, null=True)
	time = models.DateTimeField(auto_now_add=True)
	user = models.CharField(max_length=80)
	message = models.CharField(max_length=300)

	def __str__(self):
		return u'%s: %s' % (self.time, self.message)

	def color(self):
		if self.priority == 1:
			return "log_high"
		if self.priority == 2:
			return "log_medium"
		if self.priority == 3:
			return "log_low"


class Counter(models.Model):
	ip = models.GenericIPAddressField()
	time = models.DateTimeField(auto_now_add=True)
	agent = models.CharField(max_length=300)

	def __str__(self):
		return u'%s %s' % (self.ip, self.time)


class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name="profile", on_delete=models.PROTECT, null=True)
	name = models.CharField(max_length=40)
	surname = models.CharField(max_length=40, blank=True, null=True)
	DEFAULT_PAYMENT_ACCOUNT = models.IntegerField(blank=True, null=True)
	DEFAULT_EXPENCE_SUB_CATEGORY = models.IntegerField(blank=True, null=True)
	DEFAULT_DOWNPAYMENT_COMMENT = models.CharField(max_length=40, blank=True, null=True)
	DEFAULT_SALARY_COMMENT = models.CharField(max_length=40, blank=True, null=True)
	BANK_CUSTOMERID = models.CharField(max_length=512, blank=True, null=True)
	BANK_CLIENTID = models.CharField(max_length=512, blank=True, null=True)
	BANK_SECRET = models.CharField(max_length=512, blank=True, null=True)
	BANK_SECRET_EXPIRE = models.DateField(blank=True, null=True)


	def __str__(self):
		return u'%s %s' % (self.name, self.surname)

	"""
	def age(this):
		birth = this.date_birth
		if birth is None:
			return ''
		else:
			if this.is_alive:
				today = date.today()
			else:
				today = this.date_death
			try:  # raised when birth date is February 29 and the current year is not a leap year
				birthday = birth.replace(year=today.year)
			except ValueError:
				birthday = birth.replace(year=today.year, day=birth.day - 1)

			#return today.year - birth.year
			if birthday > today:
				age = today.year - birth.year - 1
			else:
				age = today.year - birth.year
			return age

	def birthday_countdown(this):
		# return number of days till birthdays
		if not this.is_alive:
			return ''
		else:
			birth = this.date_birth
			if birth is None:
				return ''
			else:
				today = date.today()
				next = compensate_leap_year(birth, today.year)

				if next >= today:  # birthday this year
					return (next - today).days
				else:  # birthday not untill next year
					next = compensate_leap_year(birth, today.year + 1)
					return (next - today).days

def compensate_leap_year(birth, to_year):
	try:
		return birth.replace(year=to_year)
	except:
		return birth.replace(year=to_year, day=birth.day - 1)
	"""


def make_custom_plugins(f):
# http://strattonbrazil.blogspot.com/2011/03/using-jquery-uis-date-picker-on-all.html
	formfield = f.formfield()
	if isinstance(f, models.DateField):
		formfield.widget.format = '%Y-%m-%d'
		formfield.widget.attrs.update({'class': 'datepicker'})

	if isinstance(f, models.ManyToManyField) or isinstance(f, models.ForeignKey):
		formfield.widget.attrs.update({'class': 'chzn-select', 'data-placeholder': 'Select tags...'})

	return formfield


class UserProfileForm(forms.ModelForm):
	formfield_callback = make_custom_plugins

	class Meta:
		model = UserProfile
		fields = "__all__"


class LoginForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)


class ResetPasswordForm(forms.Form):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(ResetPasswordForm, self).__init__(*args, **kwargs)

	old_password = forms.CharField(widget=forms.PasswordInput)
	password = forms.CharField(widget=forms.PasswordInput)
	repeat_password = forms.CharField(label='For avoiding typos', widget=forms.PasswordInput)

	def clean_repeat_password(self):
		password = self.cleaned_data['password']
		repeat_password = self.cleaned_data.get('repeat_password', None)
		if password != repeat_password:
			raise forms.ValidationError("You did not enter the same new password!")

		return repeat_password

	def clean_old_password(self):
		old_password = self.cleaned_data['old_password']
		if not self.user.check_password(old_password):
			raise forms.ValidationError("Old password is wrong!")
