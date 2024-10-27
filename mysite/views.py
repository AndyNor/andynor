from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # shortcut for is_authenticated()
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib import messages  # Message system
from django.http import HttpResponseRedirect
from django.template import RequestContext
from datetime import datetime, timedelta
from django.db.models import Count
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from mysite.site_wide_functions import get_previous_page, makeJSON, add_to_log, get_client_ip, safe_referrer
from mysite.models import UserProfile, UserProfileForm, Counter, LoginForm, ResetPasswordForm, SiteLog
from blog.models import Blog, Comment, Category
from mysite.search import get_query
from mysite.site_wide_functions import generate_form
from databases.models import Data as DBobjects
from blog.views import generate_archive_links
from blog.models import Tag  # for displaying tag cloud on front page


def my_custom_permission_denied_view(request, exception):
	messages.error(request, "Sorry, you don't have permission to perform this action.")
	return render(request, '403.html', {})


def user_not_blocked(request):  # return True if not blocked
	threshold = datetime.now() - timedelta(hours=2)
	log_entries = SiteLog.objects.filter(
		ip=get_client_ip(request),
		time__gt=threshold,
		message__contains="Failed attempt at authentication"
	)
	if len(log_entries) > 6:
		return False

	return True


def user_login(request):
	form = LoginForm()
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			if form.cleaned_data:
				if user_not_blocked(request):
					username = request.POST['username']
					password = request.POST['password']
					user = authenticate(username=username, password=password)
					if user != None:
						if user.is_active:
							login(request, user)
							user_name = user.get_full_name()
							if user_name == '':
								user_name = request.user
							messages.success(request, 'You are logged in as %s.' % user_name)
							add_to_log(request, "Successful user authentication")
							return HttpResponseRedirect(get_previous_page(request, 'root'))
						else:
							messages.error(request, 'Your are disabled.')
							add_to_log(request, "Successful user authentication, but account is blocked", 1)
					else:
						messages.error(request, 'I could not verify your identity.')
						log_message = "Failed attempt at authentication (%s)" % username
						add_to_log(request, log_message, 2)
				else:
					messages.error(request, 'I could not verify your identity.')
					log_message = "IP %s was blocked" % get_client_ip(request)
					add_to_log(request, log_message, 1)

	request.session['redirect_next'] = safe_referrer(request)
	return render(request, 'login.html', {
		'form': form,
	})


@login_required
def password_change(request):
	user = request.user
	form = ResetPasswordForm(user=user)
	if request.method == 'POST':
		form = ResetPasswordForm(request.POST, user=user)
	if form.is_valid():
		new_password = form.cleaned_data['password']
		user.set_password(new_password)
		user.save()
		add_to_log(request, "Performed a password change", 1)
		messages.success(request, "Your password has been changed!")
		return HttpResponseRedirect(get_previous_page(request, 'root'))

	header_text = "Bytt passordet for %s" % request.user.get_full_name()
	return render(request, 'form_simple.html', {
		'form': form,
		'header': header_text,
	})


def go_back(request):
	return HttpResponseRedirect(get_previous_page(request, 'root'))


def user_logout(request):
	logout(request)
	messages.info(request, 'Your session has been destroyed.')
	return HttpResponseRedirect(safe_referrer(request))


def contact_email(request):
	return render(request, 'email_form.html', {
		'form': 'test',
	})


def rss(request):
	return render(request, 'rss.html', {
		'rss': 'test',
	})


def index(request):
	all_categories = Category.objects.filter(visible=True)

	# on frontpage not special health (5), special (10), school (11) or fun (12)
	blogs = Blog.objects.exclude(
		category__in=[5, 10, 11, 12]
	).filter(
		published=True,
		linked=True
	).order_by('-origin')[0:5]

	blogs_display = []
	if blogs:
		if len(blogs) > 1:
			for blog in blogs:
				comments = Comment.objects.filter(page=blog.pk).order_by('-pk')
				blogs_display.append({"content": blog, "comments": comments})
		else:
			try:
				comments = Comment.objects.filter(page=blogs.pk).order_by('-pk')
			except:
				comments = None
			blogs_display.append({"content": blogs, "comments": comments})
	else:
		blogs_display.append({"content": None, "comments": None})

	#school_subjects = Blog.objects.filter(category=11, published=True, sticky=True).order_by('-pk')
	movies = DBobjects.objects.filter(category__name='movies').order_by('-pk')[:10]
	tvseries = DBobjects.objects.filter(category__name='tvseries').order_by('-flagged', '-pk')[:10]
	audible = DBobjects.objects.filter(category__name='audible').order_by('-pk')[:10]
	paperbooks = DBobjects.objects.filter(category__name='books').order_by('-pk')[:10]
	spotify = DBobjects.objects.filter(category__name='spotify').order_by('name')
	games = DBobjects.objects.filter(category__name='games').order_by('-pk')[:10]
	sticky_blogs = Blog.objects.filter(published=True, sticky=True).order_by('-updated')
	#profiles = list(UserProfile.objects.all())
	#profiles.sort(key=lambda x: x.birthday_countdown())

	#  Tag cloud, copy from blogs.views
	val_min = 50
	val_max = 120
	freqs = Tag.objects.annotate(frequency=Count('blog__tags'))
	if freqs:
		freq_max = freqs.order_by('-frequency')[0].frequency
		for tag in freqs:
			tag.frequency = (float(tag.frequency) / float(freq_max)) * (val_max - val_min) + val_min
	else:
		freqs = None

	return render(request, 'home.html', {
		'category_list': all_categories,
		'blogs_display': blogs_display,
		#'school_subjects': school_subjects,
		'sticky_blogs': sticky_blogs,
		'movies': movies,
		'audible': audible,
		'paperbooks': paperbooks,
		#'profiles': profiles[:5],
		'spotify': spotify,
		'games': games,
		#'archive_menu': generate_archive_links(False, False, 3),
		'tagfreqs': freqs,  # tag cloud
		'tvseries': tvseries,
	})


def count_query(history_days):
	end_time = datetime.now()
	start_time = end_time - timedelta(days=history_days)
	result = Counter.objects.filter(time__range=(start_time, end_time))
	return result


def search(request):
	query_string = ''
	found_entries = None
	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']
		entry_query = get_query(query_string, ['title', 'content'])
		valid_entries = Blog.objects.filter(published=1)
		if entry_query != None:
			found_entries = valid_entries.filter(entry_query).order_by('-pk')[:25]

	return render(request, 'search_default.html', {
		'query_string': query_string,
		'found_entries': found_entries,
	})


@permission_required('blog.blog.can_add_blog', raise_exception=True)
def profile(request):
	import operator
	from django.db.models.functions import TruncMonth
	from django.db.models import Count

	sorted_session_items = sorted(request.session.items(), key=operator.itemgetter(0), reverse=True)
	profiles = UserProfile.objects.all().order_by('surname')

	blogs = Blog.objects.values('title', 'pk', 'created', 'updated').filter(published=True)
	blogs_new = blogs.order_by('-created')[:10]
	blogs_updated = blogs.order_by('-updated')[:10]

	blogs_draft = Blog.objects.values('title', 'pk', 'created', 'updated').filter(published=False)

	logs = SiteLog.objects.order_by('-pk')[:10]
	latest_comments = Comment.objects.order_by('-pk')[:7]
	sessions = Session.objects.all()

	visits = Counter.objects.annotate(month=TruncMonth('time')).values('month').annotate(count=Count('id'))
	counter_months = []
	counter_counts = []
	for v in visits:
		counter_months.append(v["month"].strftime("%Y-%m"))
		counter_counts.append(v["count"])

	session_users = []
	for i in sessions:
		uid = i.get_decoded().get('_auth_user_id')
		active = False if (request.session.session_key != i.session_key) else True
		try:
			user = User.objects.get(pk=uid)
			session_users.append({
				#'session': i.session_key,
				'user': user,
				'active': active,
			})
		except:
			pass


	return render(request, 'profiles.html', {
		'profiles': profiles,
		'session_data': sorted_session_items,
		'blogs_new': blogs_new,
		'blogs_updated': blogs_updated,
		'blogs_draft': blogs_draft,
		'latest_comments': latest_comments,
		'current_time': datetime.now(),
		'sessions': sessions,
		'session_count': sessions.count(),
		'session_users': session_users,
		'logs': logs,
		'counter_months': counter_months,
		'counter_counts': counter_counts,
	})


@permission_required('mysite.user_profile.can_add_user_profile', raise_exception=True)
def profile_update(request):
	profile_id = request.user.profile.pk
	profile_form = generate_form(request, UserProfile, UserProfileForm, profile_id, None)
	if profile_form.is_valid():
		try:
			profile_form.save()
			return HttpResponseRedirect(reverse('profile'))
		except:
			messages.error(request, 'Could not save')
	try:
		instance = UserProfile.objects.get(pk=profile_id)
	except:
		instance = None

	return render(request, 'profiles_update.html', {
		'form': profile_form,
		'profile': instance,
	})


@permission_required('mysite.user_profile.can_add_user_profile', raise_exception=True)
def profile_delete(request, profile_id):
	entity = UserProfile.objects.get(pk=profile_id)
	entity.delete()
	return HttpResponseRedirect(reverse('profile'))


@login_required
def counter(request, year, month):
	visitors = Counter.objects.filter(time__year=year).filter(time__month=month)

	return render(request, 'counter.html', {
		'visitors': visitors,
		'year': year,
		'month': month,
	})

