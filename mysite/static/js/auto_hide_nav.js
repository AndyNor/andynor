(function () {
	'use strict';

	var TOP_HIDE_DELAY_MS = 750;
	var SCROLL_TOP_EPS = 2;

	var body = document.body;
	if (!body) {
		return;
	}
	body.classList.add('ui-autohide-enabled');

	var topNav = document.querySelector('.navbar-fixed-top');
	var bottomNav = document.getElementById('home-bottom-nav');

	var hideTimer = null;
	var isHidden = false;

	function isLightboxOpen() {
		var de = document.documentElement;
		return !!(de && de.classList && de.classList.contains('lightbox-open'));
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
		if (atTop()) {
			setHidden(false);
			return;
		}
		hideTimer = window.setTimeout(function () {
			if (isLightboxOpen()) {
				setHidden(true);
				return;
			}
			if (!atTop()) {
				setHidden(true);
			} else {
				setHidden(false);
			}
		}, TOP_HIDE_DELAY_MS);
	}

	function onActivity() {
		if (isLightboxOpen()) {
			setHidden(true);
			clearHideTimer();
			return;
		}
		setHidden(false);
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

	// Keep visible at top on initial load.
	if (atTop()) {
		setHidden(false);
	} else {
		scheduleHide();
	}

	// Scrolling: show immediately, then hide after idle.
	window.addEventListener('scroll', onActivity, { passive: true });

	// Touch/mouse/keyboard: treat as activity too (helps when user taps after scroll).
	window.addEventListener('touchstart', onActivity, { passive: true });
	window.addEventListener('mousemove', function () {
		// Mousemove can be noisy; only unhide if currently hidden.
		if (isHidden) {
			onActivity();
		}
	}, { passive: true });
	window.addEventListener('keydown', onActivity);

	attachHoverLock(topNav);
	attachHoverLock(bottomNav);

	// If user tabs into nav controls, keep it visible.
	document.addEventListener('focusin', function (e) {
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
	});

	// Watch for lightbox open/close (class on <html>).
	try {
		var mo = new MutationObserver(function () {
			if (isLightboxOpen()) {
				setHidden(true);
				clearHideTimer();
			} else {
				// On close, restore the normal behavior immediately.
				scheduleHide();
			}
		});
		mo.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
	} catch (err) {}
})();

