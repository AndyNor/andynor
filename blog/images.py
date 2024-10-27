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


def save_to_disk(image, image_object):
# change temp folder for uploaded stuff
	folder = '%soriginals/' % (settings.MEDIA_ROOT)
	filebase = new_image_filename()
	extention = str(image).split('.')[-1]
	filename = '%s.%s' % (filebase, extention)
	path = '%s%s' % (folder, filename)
	try:
		with open(path, 'wb+') as destination:
			for chunk in image.chunks():
				destination.write(chunk)
		image_object.original = filename
		return filename
	except:
		return False


def delete_original(request, image):
	path = '%soriginals/%s' % (settings.MEDIA_ROOT, image.original)
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
	original = '%soriginals/%s' % (settings.MEDIA_ROOT, image.original)
	filename_large = 'large_%s' % image.original
	try:
		im = Image.open(original)
	except:
		return False

	im = ImageOps.exif_transpose(im)

	if im.size[0] > max_width:
		height = int((float(max_width * 0.625) / float(im.size[0])) * float(im.size[1]))  # >1920 gir 1200x bilder
		im.thumbnail((max_width, height), Image.ANTIALIAS)
	im.save('%s%s' % (settings.MEDIA_ROOT, filename_large), im.format, quality=94)
	image.large = filename_large
	image.save()
	return True


''' functions directly used by the views '''


def img_calc_thumb(request, image, max_width, max_height=False):

	def reduce_wide(im, background, new_size):
		im.thumbnail(new_size, Image.ANTIALIAS)
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
		im.thumbnail(new_size, Image.ANTIALIAS)
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
	filename_thumb = image.original if (image.original != None) else image.large
	filename_thumb = 'thumb_%s.%s' % (filename_thumb, "jpg")

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
		im.thumbnail((max_width, new_height), Image.ANTIALIAS)

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
	new_filename = save_to_disk(filename, img)
	if new_filename:  # if file was moved to archive
		img.save()
		image_order_cleanup(blog_id)
		img_calc_large(img, 3840)
		img_calc_thumb(request, img, 400, 266)
		return True
	else:
		return False


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
