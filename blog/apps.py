from django.apps import AppConfig


class BlogConfig(AppConfig):
	name = 'blog'

	def ready(self):
		try:
			from pillow_heif import register_heif_opener

			register_heif_opener()
		except ImportError:
			pass
