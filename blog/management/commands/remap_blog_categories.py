# -*- coding: utf-8 -*-
from __future__ import annotations

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from blog.models import Blog, Category, Tag


class Command(BaseCommand):
	help = (
		"Remap blog categories by ID and add original category as a tag.\n\n"
		"Mapping (based on production IDs provided):\n"
		"- gadgets (3) -> hverdags (1)\n"
		"- web (6) -> hverdags (1)\n"
		"- økonomi (7) + vitenskap (9) + helse (5) -> hverdags (1)\n"
		"- skole (11) -> (unchanged)\n"
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--apply",
			action="store_true",
			help="Actually write changes to the database. Without this flag it's a dry-run.",
		)

	def handle(self, *args, **options):
		apply_changes = bool(options["apply"])

		# Source category id -> destination category id
		remap = {
			3: 1,  # gadgets -> hverdags
			6: 1,  # web -> hverdags
			7: 1,  # økonomi -> hverdags
			9: 1,  # vitenskap -> hverdags
			5: 1,  # helse -> hverdags
		}

		categories = {c.id: c for c in Category.objects.filter(id__in=set(remap.keys()) | set(remap.values()))}
		missing = sorted((set(remap.keys()) | set(remap.values())) - set(categories.keys()))
		if missing:
			raise CommandError(f"Missing Category IDs in DB: {missing}")

		blogs = (
			Blog.objects.select_related("category")
			.prefetch_related("tags")
			.filter(category_id__in=remap.keys())
		)

		changed = 0
		by_mapping = defaultdict(int)

		def process():
			nonlocal changed
			for blog in blogs:
				old_cat = blog.category
				new_cat_id = remap.get(old_cat_id := old_cat.id)
				if not new_cat_id:
					continue
				if new_cat_id == old_cat_id:
					continue

				# Add original category name as an extra tag
				tag_text = (old_cat.category or "").strip().lower()
				if tag_text:
					tag_obj, _created = Tag.objects.get_or_create(tag=tag_text, defaults={"description": ""})
					blog.tags.add(tag_obj)

				blog.category_id = new_cat_id
				if apply_changes:
					blog.save(update_fields=["category"])

				changed += 1
				by_mapping[(old_cat_id, new_cat_id)] += 1

				self.stdout.write(
					f"{'UPDATED' if apply_changes else 'WOULD UPDATE'} "
					f"Blog id={blog.id}: {categories[old_cat_id].category} ({old_cat_id}) -> "
					f"{categories[new_cat_id].category} ({new_cat_id}); "
					f"tag +='{tag_text}'"
				)

		if apply_changes:
			with transaction.atomic():
				process()
		else:
			process()

		self.stdout.write("")
		self.stdout.write("Oppsummert (flyttet blogginnlegg fra kategori til kategori):")
		for (src, dst), count in sorted(by_mapping.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])):
			self.stdout.write(
				f"{count} blogginnlegg: {categories[src].category} ({src}) -> {categories[dst].category} ({dst})"
			)
		self.stdout.write(f"Total: {changed} {'updated' if apply_changes else 'to update'}")
		if not apply_changes:
			self.stdout.write("")
			self.stdout.write("Dry-run: ingen endringer ble lagret i databasen.")
			self.stdout.write("Kjør følgende for å utføre oppdateringen:")
			self.stdout.write("  python manage.py remap_blog_categories --apply")
