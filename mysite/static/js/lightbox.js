(function () {
	function closest(el, selector) {
		while (el && el.nodeType === 1) {
			if (el.matches(selector)) return el;
			el = el.parentElement;
		}
		return null;
	}

	function enableDragPan(overlay) {
		if (!overlay || overlay._dragPanBound) return;
		overlay._dragPanBound = true;

		var isDown = false;
		var moved = false;
		var startX = 0;
		var startY = 0;
		var startScrollLeft = 0;
		var startScrollTop = 0;
		var figure = null;

		function onDown(e) {
			var ov = document.getElementById('site-lightbox');
			if (!ov || ov.classList.contains('is-hidden') || !ov.classList.contains('is-zoomed')) return;
			var img = closest(e.target, '.lightbox-img');
			if (!img) return;
			figure = ov.querySelector('.lightbox-figure');
			if (!figure) return;

			isDown = true;
			moved = false;
			startX = e.clientX;
			startY = e.clientY;
			startScrollLeft = figure.scrollLeft;
			startScrollTop = figure.scrollTop;
			try { img.setPointerCapture(e.pointerId); } catch (err) {}
			e.preventDefault();
		}

		function onMove(e) {
			if (!isDown || !figure) return;
			var dx = e.clientX - startX;
			var dy = e.clientY - startY;
			if (!moved && (Math.abs(dx) > 6 || Math.abs(dy) > 6)) {
				moved = true;
			}
			figure.scrollLeft = startScrollLeft - dx;
			figure.scrollTop = startScrollTop - dy;
		}

		function onUp(e) {
			if (!isDown) return;
			isDown = false;
			if (moved) {
				// Suppress the click that follows a drag (prevents toggling zoom)
				overlay._suppressClickUntil = Date.now() + 350;
			}
			moved = false;
			figure = null;
		}

		document.addEventListener('pointerdown', onDown, { passive: false });
		document.addEventListener('pointermove', onMove, { passive: true });
		document.addEventListener('pointerup', onUp, { passive: true });
		document.addEventListener('pointercancel', onUp, { passive: true });
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
		enableDragPan(overlay);
		return overlay;
	}

	function openLightbox(anchor) {
		var overlay = ensureLightbox();
		var img = overlay.querySelector('.lightbox-img');
		var cap = overlay.querySelector('.lightbox-caption');
		overlay.classList.remove('is-zoomed');

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

			overlay.classList.remove('is-zoomed');
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
		overlay.classList.remove('is-zoomed');
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
		// Toggle "fullscreen" (prioritize height) by tapping/clicking the image.
		var overlay = document.getElementById('site-lightbox');
		if (overlay && !overlay.classList.contains('is-hidden')) {
			var sup = overlay._suppressClickUntil || 0;
			if (sup && Date.now() < sup) {
				return;
			}
			var lbImg = closest(e.target, '.lightbox-img');
			if (lbImg) {
				e.preventDefault();
				var willZoom = !overlay.classList.contains('is-zoomed');
				// Remember where inside the image the user clicked, so zoom starts near that area.
				var clickRatioX = 0.5;
				var clickRatioY = 0.5;
				try {
					var r = lbImg.getBoundingClientRect();
					if (r && r.width > 0 && r.height > 0) {
						clickRatioX = (e.clientX - r.left) / r.width;
						clickRatioY = (e.clientY - r.top) / r.height;
						clickRatioX = Math.max(0, Math.min(1, clickRatioX));
						clickRatioY = Math.max(0, Math.min(1, clickRatioY));
					}
				} catch (err) {}

				// Make horizontal intent obvious: snap to left / center / right thirds.
				// - left third -> show left edge
				// - right third -> show right edge
				// - middle third -> center
				var snappedX = 0.5;
				if (clickRatioX <= (1 / 3)) snappedX = 0;
				else if (clickRatioX >= (2 / 3)) snappedX = 1;
				else snappedX = 0.5;

				overlay.classList.toggle('is-zoomed');
				if (willZoom) {
					var applyPan = function () {
						var fig = overlay.querySelector('.lightbox-figure');
						if (!fig) return;
						var maxX = Math.max(0, fig.scrollWidth - fig.clientWidth);
						var maxY = Math.max(0, fig.scrollHeight - fig.clientHeight);
						if (maxX > 0) {
							overlay.classList.add('is-overflow-x');
						} else {
							overlay.classList.remove('is-overflow-x');
						}
						fig.scrollLeft = Math.round(maxX * snappedX);
						fig.scrollTop = Math.round(maxY * clickRatioY);
					};

					// After layout updates for zoomed mode, pan the scroll container.
					window.requestAnimationFrame(function () {
						window.requestAnimationFrame(function () {
							applyPan();
						});
					});

					// iOS Safari: image/layout might not be ready immediately; apply again on load.
					if (!lbImg.complete) {
						var onLoad = function () {
							lbImg.removeEventListener('load', onLoad);
							window.requestAnimationFrame(function () { applyPan(); });
							window.setTimeout(applyPan, 30);
						};
						lbImg.addEventListener('load', onLoad);
					} else {
						window.setTimeout(applyPan, 30);
					}
				}
				return;
			}
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

