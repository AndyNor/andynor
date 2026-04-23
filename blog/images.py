from django.contrib import messages  # Message system
from django.conf import settings  # Get the media_root variable
from PIL import Image
import errno
import os
import string
import random
from datetime import datetime
from blog import models as blog_models
from mysite.site_wide_functions import silentremove
from PIL import ImageOps


try:
	# Pillow >= 10
	RESAMPLE_LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
	# Pillow < 10
	RESAMPLE_LANCZOS = Image.LANCZOS


def image_exists(request, image_id):
	try:
		image = blog_models.Image.objects.get(pk=image_id)
	except:
		messages.error(request, 'Image not in dB')
		return False
	path = '%s%s' % (settings.MEDIA_ROOT, image.large)
	if os.path.isfile(path):
		return image
	else:
		messages.error(request, 'Image not on disk')
		return False


def new_image_filename():
	now = datetime.now()
	now_string = now.strftime('%Y-%m-%d_%H%M%S')

	def random_string(length, alphabet=string.ascii_lowercase + string.digits):
		return ''.join(random.choice(alphabet) for x in range(length))

	random_number = random_string(16)
	return '%s_%s' % (now_string, random_number)


def _ensure_media_root_exists():
	try:
		os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
	except Exception:
		return False
	return True


def save_large_from_upload(uploaded_file, image_object, max_width):
	"""
	Saves only a processed large image to MEDIA_ROOT (no originals copy).
	Returns True/False.
	"""
	if not _ensure_media_root_exists():
		return False

	base = new_image_filename()
	image_object.original = base  # used as stable id / basename (no file stored)
	image_object.large = 'large_%s.jpg' % base

	try:
		im = Image.open(uploaded_file)
	except Exception:
		return False

	im = ImageOps.exif_transpose(im)

	# resize if needed (limit by width)
	try:
		width, height = im.size
	except Exception:
		return False

	if width > max_width:
		new_height = int((float(max_width) / float(width)) * float(height))
		im.thumbnail((max_width, new_height), RESAMPLE_LANCZOS)

	large_path = '%s%s' % (settings.MEDIA_ROOT, image_object.large)
	try:
		rgb_im = im.convert('RGB')
		rgb_im.save(large_path, "jpeg", quality=94)
	except Exception:
		return False

	image_object.save()
	return True


def delete_original(request, image):
	# New behavior: we don't store originals anymore.
	# Backwards-compatible cleanup for older rows that still have originals on disk.
	if not image.original:
		return

	# Older rows stored full filename with extension in originals/
	candidates = []
	candidates.append('%soriginals/%s' % (settings.MEDIA_ROOT, image.original))

	# If original is a basename without extension, try a few common ones
	if '.' not in str(image.original):
		for ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
			candidates.append('%soriginals/%s%s' % (settings.MEDIA_ROOT, image.original, ext))

	for path in candidates:
		silentremove(request, path)


def delete_large(request, image):
	path = '%s%s' % (settings.MEDIA_ROOT, image.large)
	silentremove(request, path)


def delete_thumbnail(request, image):
	path = '%s%s' % (settings.MEDIA_ROOT, image.thumbnail)
	silentremove(request, path)


def highest_order_nr(blog_id):
	try:
		highest_order = blog_models.Image.objects.values('order').filter(blog=blog_id).order_by('-order')[0]['order']
	except:
		highest_order = 0
	return highest_order


def image_order_cleanup(blog_id):
	images = blog_models.Image.objects.filter(blog=blog_id).order_by('order')
	counter = 1
	for image in images:
		image.order = counter
		image.save()
		counter += 1


def img_calc_large(image, max_width):
	# Prefer original (legacy), otherwise resize from existing large.
	original_path = '%soriginals/%s' % (settings.MEDIA_ROOT, image.original) if image.original else None
	large_path = '%s%s' % (settings.MEDIA_ROOT, image.large)

	im = None
	if original_path and os.path.isfile(original_path):
		try:
			im = Image.open(original_path)
		except Exception:
			im = None
	if im is None:
		if not os.path.isfile(large_path):
			return False
		try:
			im = Image.open(large_path)
		except Exception:
			return False

	im = ImageOps.exif_transpose(im)

	if im.size[0] > max_width:
		new_height = int((float(max_width) / float(im.size[0])) * float(im.size[1]))
		im.thumbnail((max_width, new_height), RESAMPLE_LANCZOS)

	# overwrite current large (don't create additional files)
	rgb_im = im.convert('RGB')
	rgb_im.save(large_path, "jpeg", quality=94)
	image.save()
	return True


''' functions directly used by the views '''


def img_calc_thumb(request, image, max_width, max_height=False):

	def reduce_wide(im, background, new_size):
		im.thumbnail(new_size, RESAMPLE_LANCZOS)
		height = im.size[1]
		width = im.size[0]
		#print("asked for size: %s %s" % (new_size))
		#print("actual size: %s %s" % (width, height))
		middle = int(width / 2)
		delta = int(max_width / 2)
		x_min = middle - delta
		x_max = middle + delta
		#print("%s %s %s %s") % (x_min, 0, x_max, thumb_height)
		crop = im.crop((x_min, 0, x_max, height)) # left, upper, right, lower)-tuple
		crop.load()
		background.paste(crop, (0, 0))
		print("%s : %s" % ((x_min, 0, x_max, height), (background.size[0], background.size[1])))
		return background

	def reduce_tall(im, background, new_size):
		im.thumbnail(new_size, RESAMPLE_LANCZOS)
		height = im.size[1]
		width = im.size[0]
		#print("asked for size: %s %s" % (new_size))
		#print("actual size: %s %s" % (width, height))
		middle = int(height / 2)
		delta = int(max_height / 2)
		y_min = middle - delta
		y_max = middle + delta # + (max_height - (delta * 2))  # last + is adjustment for making exactly size
		#print("%s %s %s %s") % (0, y_min, width, y_max)
		#crop = im.crop((0, y_min, width, y_max))
		crop = im.crop((0, y_min, width, y_max)) # left, upper, right, lower)-tuple
		crop.load()
		background.paste(crop, (0, 0))
		print("%s : %s" % ((0, y_min, width, y_max), (background.size[0], background.size[1])))
		return background

	# open large version of image
	filename_large = '%s%s' % (settings.MEDIA_ROOT, image.large)
	try:
		im = Image.open(filename_large)
	except:
		messages.error(request, 'Could not find a large version of image')
		return False

	im = ImageOps.exif_transpose(im)

	# determine thumbnail filename
	if image.original:
		base = image.original if '.' not in str(image.original) else os.path.splitext(str(image.original))[0]
	else:
		# large_<base>.jpg -> <base>
		large_base = os.path.splitext(os.path.basename(str(image.large)))[0]
		base = large_base[6:] if large_base.startswith('large_') else large_base
	filename_thumb = 'thumb_%s.jpg' % base

	# create a background
	if max_height:
		background = Image.new('RGB', (max_width, max_height), (255, 255, 255))

	# find width and height of large image
	width = im.size[0]
	height = im.size[1]
	#print((width, height))

	# determine if image is tall or wide
	if not max_height:
		# don't care about height
		new_height = int((width / max_width) * height)
		im.thumbnail((max_width, new_height), RESAMPLE_LANCZOS)

	else:
		if width >= (height * (max_width / float(max_height))):
			# image is too wide
			new_height = max_height
			new_width = int((height / max_height) * width)
			im = reduce_wide(im, background, (new_width, new_height))
		else:
			#image is too tall
			new_width = max_width
			new_height = int((width / max_width) * height)
			im = reduce_tall(im, background, (new_width, new_height))

	# paste reduced image onto background
	thumb_path = '%s%s' % (settings.MEDIA_ROOT, filename_thumb)
	rgb_im = im.convert('RGB')
	rgb_im.save(thumb_path, "jpeg", quality=85)
	messages.success(request, 'Thumbnail was recalculated')
	image.thumbnail = filename_thumb
	image.save()


def images_create(request, blog_id, user, filename, image_id):
	if image_id is False:
		img = blog_models.Image()
		img.owner = user
		img.blog = blog_models.Blog.objects.get(pk=blog_id)
		img.order = highest_order_nr(blog_id) + 1
	else:
		img = blog_models.Image.objects.get(pk=image_id)
		#print 'image %s' % img
		delete_original(request, img)
		delete_large(request, img)
		delete_thumbnail(request, img)

	img.filename = filename.name[:50]
	# Save only processed versions (no originals stored)
	if not save_large_from_upload(filename, img, 3840):
		return False

	image_order_cleanup(blog_id)
	img_calc_thumb(request, img, 400, 266)
	return True


def images_remove(request, image_id):
	try:
		image = blog_models.Image.objects.get(pk=image_id)
	except:
		messages.error(request, 'Image ID could not be found')
		return

	blog_id = image.blog
	try:
		delete_original(request, image)
	except:
		messages.error(request, 'Could not delete original image')

	try:
		delete_large(request, image)
	except:
		messages.error(request, 'Could not delete large version of image')

	try:
		delete_thumbnail(request, image)
	except:
		messages.error(request, 'Could not delete thumbnail image')

	try:
		image.delete()
		image_order_cleanup(blog_id)
	except:
		messages.error(request, 'Could not remove image %s from database' % image.pk)
