(function () {
	function closest(el, selector) {
		while (el && el.nodeType === 1) {
			if (el.matches(selector)) return el;
			el = el.parentElement;
		}
		return null;
	}

	function ensureLightbox() {
		var existing = document.getElementById('site-lightbox');
		if (existing) return existing;

		var overlay = document.createElement('div');
		overlay.id = 'site-lightbox';
		overlay.className = 'lightbox-overlay is-hidden';
		overlay.setAttribute('role', 'dialog');
		overlay.setAttribute('aria-modal', 'true');
		overlay.setAttribute('aria-label', 'Bildevisning');

		overlay.innerHTML =
			'<div class="lightbox-backdrop" data-action="close" aria-hidden="true"></div>' +
			'<div class="lightbox-panel" role="document">' +
				'<button type="button" class="lightbox-close" data-action="close" aria-label="Lukk (Esc)">&times;</button>' +
				'<button type="button" class="lightbox-nav lightbox-nav--prev" data-action="prev" aria-label="Forrige bilde">&#10094;</button>' +
				'<button type="button" class="lightbox-nav lightbox-nav--next" data-action="next" aria-label="Neste bilde">&#10095;</button>' +
				'<figure class="lightbox-figure">' +
					'<img class="lightbox-img" alt="">' +
					'<figcaption class="lightbox-caption"></figcaption>' +
				'</figure>' +
			'</div>';

		document.body.appendChild(overlay);
		return overlay;
	}

	function openLightbox(anchor) {
		var overlay = ensureLightbox();
		var img = overlay.querySelector('.lightbox-img');
		var cap = overlay.querySelector('.lightbox-caption');

		var gallery = anchor.getAttribute('data-gallery') || '';
		var anchors = [];
		if (gallery) {
			anchors = Array.prototype.slice.call(document.querySelectorAll('a.js-lightbox[data-gallery="' + gallery.replace(/"/g, '\\"') + '"]'));
		} else {
			anchors = [anchor];
		}
		var idx = Math.max(0, anchors.indexOf(anchor));

		function showAt(i) {
			if (!anchors.length) return;
			if (i < 0) i = 0;
			if (i >= anchors.length) i = anchors.length - 1;
			idx = i;

			var a = anchors[idx];
			var href = a.getAttribute('href') || '';
			var caption = a.getAttribute('data-caption') || '';

			img.src = href;
			img.alt = caption || 'Bilde';
			cap.textContent = caption;

			var prevBtn = overlay.querySelector('[data-action="prev"]');
			var nextBtn = overlay.querySelector('[data-action="next"]');
			if (prevBtn) prevBtn.disabled = idx <= 0;
			if (nextBtn) nextBtn.disabled = idx >= anchors.length - 1;
		}

		overlay._lightboxState = {
			anchors: anchors,
			showAt: showAt,
			close: function () { closeLightbox(); },
		};

		showAt(idx);

		overlay.classList.remove('is-hidden');
		overlay.classList.add('is-open');
		document.documentElement.classList.add('lightbox-open');

		// Focus close button for accessibility
		var closeBtn = overlay.querySelector('.lightbox-close');
		if (closeBtn) closeBtn.focus();
	}

	function closeLightbox() {
		var overlay = document.getElementById('site-lightbox');
		if (!overlay) return;
		overlay.classList.add('is-hidden');
		overlay.classList.remove('is-open');
		document.documentElement.classList.remove('lightbox-open');

		var img = overlay.querySelector('.lightbox-img');
		if (img) img.src = '';
	}

	function handleOverlayAction(target) {
		var overlay = document.getElementById('site-lightbox');
		if (!overlay || overlay.classList.contains('is-hidden')) return;
		var state = overlay._lightboxState;
		var actionEl = closest(target, '[data-action]');
		if (!actionEl) return;
		var action = actionEl.getAttribute('data-action');
		if (!action) return;

		if (action === 'close') {
			closeLightbox();
			return;
		}
		if (!state || !state.showAt) return;

		var anchors = state.anchors || [];
		var img = overlay.querySelector('.lightbox-img');
		var currentSrc = img ? img.src : '';
		var idx = 0;
		for (var i = 0; i < anchors.length; i++) {
			if ((anchors[i].href || '') === currentSrc) {
				idx = i;
				break;
			}
		}
		if (action === 'prev') state.showAt(idx - 1);
		if (action === 'next') state.showAt(idx + 1);
	}

	document.addEventListener('click', function (e) {
		var a = closest(e.target, 'a.js-lightbox');
		if (a) {
			// allow modifiers to open in new tab if desired
			if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
			e.preventDefault();
			openLightbox(a);
			return;
		}
		if (closest(e.target, '#site-lightbox')) {
			handleOverlayAction(e.target);
		}
	}, true);

	document.addEventListener('keydown', function (e) {
		var overlay = document.getElementById('site-lightbox');
		if (!overlay || overlay.classList.contains('is-hidden')) return;

		if (e.key === 'Escape') {
			e.preventDefault();
			closeLightbox();
			return;
		}
		if (e.key === 'ArrowLeft') {
			e.preventDefault();
			handleOverlayAction(overlay.querySelector('[data-action="prev"]'));
			return;
		}
		if (e.key === 'ArrowRight') {
			e.preventDefault();
			handleOverlayAction(overlay.querySelector('[data-action="next"]'));
			return;
		}
	});
})();

