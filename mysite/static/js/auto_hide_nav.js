(function () {
	'use strict';

	var TOP_HIDE_DELAY_MS = 2000;
	var SCROLL_TOP_EPS = 2;
	// Match Bootstrap 2 desktop breakpoint (bootstrap-responsive.css uses 979px max-width).
	var DESKTOP_MIN_WIDTH_PX = 980;

	var body = document.body;
	if (!body) {
		return;
	}

	var topNav = document.querySelector('.navbar-fixed-top');
	var bottomNav = document.getElementById('home-bottom-nav');

	var hideTimer = null;
	var isHidden = false;
	var isAttached = false;
	var mo = null;

	var mql = null;
	try {
		mql = window.matchMedia ? window.matchMedia('(min-width: ' + String(DESKTOP_MIN_WIDTH_PX) + 'px)') : null;
	} catch (e) {
		mql = null;
	}

	function isLightboxOpen() {
		var de = document.documentElement;
		return !!(de && de.classList && de.classList.contains('lightbox-open'));
	}

	function isDesktop() {
		if (mql) {
			return !!mql.matches;
		}
		return (window.innerWidth || 0) >= DESKTOP_MIN_WIDTH_PX;
	}

	function atTop() {
		return (window.scrollY || window.pageYOffset || 0) <= SCROLL_TOP_EPS;
	}

	function setHidden(nextHidden) {
		if (!topNav && !bottomNav) {
			return;
		}
		// When photo preview/fullscreen overlay is active, keep menus hidden.
		if (isLightboxOpen()) {
			nextHidden = true;
		}
		if (nextHidden === isHidden) {
			return;
		}
		isHidden = nextHidden;
		if (isHidden) {
			body.classList.add('ui-autohide-hidden');
		} else {
			body.classList.remove('ui-autohide-hidden');
		}
	}

	function clearHideTimer() {
		if (hideTimer) {
			window.clearTimeout(hideTimer);
			hideTimer = null;
		}
	}

	function scheduleHide() {
		clearHideTimer();
		if (isLightboxOpen()) {
			setHidden(true);
			return;
		}
		// Mobile behavior: keep the extra icon row hidden unless we're at the very top.
		setHidden(!atTop());
	}

	function onActivity() {
		if (isLightboxOpen()) {
			setHidden(true);
			clearHideTimer();
			return;
		}
		// Mobile behavior: never "show on scroll". Only show again when at top.
		scheduleHide();
	}

	function attachHoverLock(el) {
		if (!el) {
			return;
		}
		el.addEventListener('mouseenter', function () {
			if (isLightboxOpen()) {
				setHidden(true);
				clearHideTimer();
				return;
			}
			// While hovering the menu, keep it visible and pause auto-hide.
			setHidden(false);
			clearHideTimer();
		});
		el.addEventListener('mouseleave', function () {
			if (isLightboxOpen()) {
				setHidden(true);
				clearHideTimer();
				return;
			}
			// Resume normal idle behavior after leaving the menu.
			scheduleHide();
		});
	}

	function onMouseMove() {
		// Mousemove can be noisy; only unhide if currently hidden.
		if (isHidden) {
			onActivity();
		}
	}

	function onFocusIn(e) {
		if (isLightboxOpen()) {
			setHidden(true);
			clearHideTimer();
			return;
		}
		var t = e && e.target;
		if (!t) {
			return;
		}
		if ((topNav && topNav.contains(t)) || (bottomNav && bottomNav.contains(t))) {
			onActivity();
		}
	}

	function enableAutoHide() {
		if (isAttached) {
			return;
		}
		body.classList.add('ui-autohide-enabled');

		// Initial state: hide unless at top.
		scheduleHide();

		// Scrolling: keep hidden unless at top.
		window.addEventListener('scroll', onActivity, { passive: true });

		// Touch/mouse/keyboard: treat as activity too (keeps state in sync).
		window.addEventListener('touchstart', onActivity, { passive: true });
		window.addEventListener('mousemove', onMouseMove, { passive: true });
		window.addEventListener('keydown', onActivity);

		attachHoverLock(topNav);
		attachHoverLock(bottomNav);

		// If user tabs into nav controls, keep it visible.
		document.addEventListener('focusin', onFocusIn);

		// Watch for lightbox open/close (class on <html>).
		try {
			mo = new MutationObserver(function () {
				if (isLightboxOpen()) {
					setHidden(true);
					clearHideTimer();
				} else {
					// On close, restore the normal behavior immediately.
					scheduleHide();
				}
			});
			mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
		} catch (err) {
			mo = null;
		}

		isAttached = true;
	}

	function disableAutoHide() {
		// Always leave menus visible on desktop.
		clearHideTimer();
		setHidden(false);
		body.classList.remove('ui-autohide-hidden');
		body.classList.remove('ui-autohide-enabled');

		if (!isAttached) {
			return;
		}
		window.removeEventListener('scroll', onActivity);
		window.removeEventListener('touchstart', onActivity);
		window.removeEventListener('mousemove', onMouseMove);
		window.removeEventListener('keydown', onActivity);
		document.removeEventListener('focusin', onFocusIn);

		if (mo) {
			try { mo.disconnect(); } catch (e) {}
			mo = null;
		}
		isAttached = false;
	}

	function applyResponsiveMode() {
		if (isDesktop()) {
			disableAutoHide();
		} else {
			enableAutoHide();
		}
	}

	applyResponsiveMode();
	if (mql && typeof mql.addEventListener === 'function') {
		mql.addEventListener('change', applyResponsiveMode);
	} else if (mql && typeof mql.addListener === 'function') {
		// Legacy Safari/old browsers.
		mql.addListener(applyResponsiveMode);
	} else {
		window.addEventListener('resize', applyResponsiveMode, { passive: true });
	}
})();

