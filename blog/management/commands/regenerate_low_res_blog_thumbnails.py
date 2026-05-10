# -*- coding: utf-8 -*-
from __future__ import annotations

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from blog.images import regenerate_blog_thumbnail
from blog.models import Image as BlogImage

# Target boxed preview (images_create / img_rethumb); does not change blog.images API.
TARGET_THUMB_WIDTH = 400
TARGET_THUMB_HEIGHT = 266

# Pre-2016-ish boxed thumbnails were 200px wide (height varies with aspect ratio).
DEFAULT_LEGACY_THUMB_WIDTH = 200


def _thumb_pixel_size(image: BlogImage) -> tuple[int, int] | None:
	"""Return (width, height) of the thumbnail file, or None if missing/unreadable."""
	if not image.thumbnail:
		return None
	path = "%s%s" % (settings.MEDIA_ROOT, image.thumbnail)
	if not os.path.isfile(path):
		return None
	try:
		with Image.open(path) as im:
			return im.size
	except Exception:
		return None


class Command(BaseCommand):
	help = (
		"Regenerate standard blog thumbnails only when the existing thumbnail file is "
		"the legacy width (default 200px wide, height varies). Leaves other thumbnails "
		"(including large/'fullthumb' variants) unchanged. Does not modify large images "
		"or thumbnail regeneration code."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--apply",
			action="store_true",
			help="Write new thumbnail files. Without this flag, only reports what would change.",
		)
		parser.add_argument(
			"--legacy-width",
			type=int,
			default=DEFAULT_LEGACY_THUMB_WIDTH,
			help=(
				"Only regenerate when the current thumbnail image is exactly this many pixels wide "
				f"(default {DEFAULT_LEGACY_THUMB_WIDTH})."
			),
		)
		parser.add_argument(
			"--limit",
			type=int,
			default=None,
			help="Process at most this many candidate images (useful for testing).",
		)

	def handle(self, *args, **options):
		apply_changes = bool(options["apply"])
		legacy_w = int(options["legacy_width"])
		limit = options["limit"]

		qs = (
			BlogImage.objects.exclude(thumbnail__isnull=True)
			.exclude(thumbnail="")
			.order_by("pk")
		)
		if limit is not None:
			qs = qs[: int(limit)]

		would_regen = 0
		done = 0
		skipped_other_width = 0
		skipped_no_large = 0
		failed = 0

		for image in qs:
			large_path = "%s%s" % (settings.MEDIA_ROOT, image.large)
			if not os.path.isfile(large_path):
				skipped_no_large += 1
				self.stderr.write(
					self.style.WARNING(
						"Image id=%s: large file missing (%s), skip" % (image.pk, image.large)
					)
				)
				continue

			size = _thumb_pixel_size(image)
			if size is None or size[0] != legacy_w:
				skipped_other_width += 1
				if options["verbosity"] >= 2:
					self.stdout.write(
						"Image id=%s: thumb size=%s (want width exactly %s), skip"
						% (image.pk, size, legacy_w)
					)
				continue

			would_regen += 1
			if not apply_changes:
				self.stdout.write(
					"WOULD regenerate image id=%s blog_id=%s thumb=%s (%sx%s)"
					% (image.pk, image.blog_id, image.thumbnail, size[0], size[1])
				)
				continue

			if regenerate_blog_thumbnail(image, TARGET_THUMB_WIDTH, TARGET_THUMB_HEIGHT):
				done += 1
				self.stdout.write(
					self.style.SUCCESS(
						"Regenerated image id=%s blog_id=%s -> %s"
						% (image.pk, image.blog_id, image.thumbnail)
					)
				)
			else:
				failed += 1
				self.stderr.write(
					self.style.ERROR("Failed image id=%s (regenerate_blog_thumbnail)" % image.pk)
				)

		self.stdout.write("")
		self.stdout.write(
			"Summary: skipped (thumb width not %s)=%s skipped (no large)=%s "
			"would_regenerate=%s regenerated=%s failed=%s"
			% (legacy_w, skipped_other_width, skipped_no_large, would_regen, done, failed)
		)
		if not apply_changes and would_regen:
			self.stdout.write("")
			self.stdout.write("Dry-run: no files were written. Run with --apply to regenerate.")
