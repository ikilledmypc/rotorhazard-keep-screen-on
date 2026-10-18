/* Keep Screen On - RotorHazard plugin. Uses NoSleep.js (MIT, Rich Tibbett). */
(function () {
	'use strict';
	if (window.__keepScreenOnLoaded || typeof NoSleep === 'undefined') return;
	window.__keepScreenOnLoaded = true;

	var KEY = 'rh_keep_screen_on';
	var noSleep = new NoSleep();
	var state = 'off'; // off | on | pending

	function load() {
		try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; }
	}
	function save(v) {
		try { localStorage.setItem(KEY, v ? '1' : '0'); } catch (e) { /* ignore */ }
	}

	var css = document.createElement('style');
	css.textContent =
		'#kso-btn{position:fixed;right:.75rem;bottom:.75rem;z-index:190;width:3rem;height:3rem;' +
		'border-radius:50%;border:2px solid rgba(255,255,255,.6);padding:0;margin:0;cursor:pointer;' +
		'display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.4);' +
		'-webkit-tap-highlight-color:transparent;transition:background-color .2s,opacity .2s;opacity:.55;background:#555;}' +
		'#kso-btn svg{width:1.6rem;height:1.6rem;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;}' +
		'#kso-btn.kso-on{background:#2e9e44;opacity:.9;}' +
		'#kso-btn.kso-pending{background:#d48a00;opacity:.9;animation:kso-pulse 1.6s infinite;}' +
		'@keyframes kso-pulse{50%{opacity:.5}}' +
		'@media print{#kso-btn{display:none}}';
	document.head.appendChild(css);

	var btn = document.createElement('button');
	btn.id = 'kso-btn';
	btn.type = 'button';
	// Simple phone-with-sun icon
	btn.innerHTML =
		'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="2" width="10" height="20" rx="2"/>' +
		'<circle cx="12" cy="11" r="2.5"/><path d="M12 6.5v.5M12 15v.5M7.5 11H8M16 11h.5"/></svg>';
	document.body.appendChild(btn);

	function render() {
		btn.className = state === 'on' ? 'kso-on' : (state === 'pending' ? 'kso-pending' : '');
		var label = state === 'on' ? 'Screen stays on (tap to turn off)' :
			state === 'pending' ? 'Keep screen on: tap anywhere to resume' :
			'Keep screen on: off (tap to turn on)';
		btn.title = label;
		btn.setAttribute('aria-label', label);
		btn.setAttribute('aria-pressed', state === 'on' ? 'true' : 'false');
	}

	function enable() {
		var p;
		try { p = noSleep.enable(); } catch (e) { p = Promise.reject(e); }
		return Promise.resolve(p).then(function () {
			state = 'on';
			render();
		}, function (err) {
			if (window.console) console.warn('Keep Screen On: could not enable', err);
			state = load() ? 'pending' : 'off';
			if (state === 'pending') armGesture();
			render();
		});
	}

	function disable() {
		try { noSleep.disable(); } catch (e) { /* ignore */ }
		state = 'off';
		render();
	}

	// Browsers require a user gesture to start the wake-lock video after each page load.
	var armed = false;
	function onGesture(ev) {
		if (ev && ev.target && btn.contains(ev.target)) return; // button handles itself
		disarmGesture();
		if (load() && state !== 'on') enable();
	}
	function armGesture() {
		if (armed) return;
		armed = true;
		document.addEventListener('click', onGesture, true);
		document.addEventListener('touchend', onGesture, true);
		document.addEventListener('keydown', onGesture, true);
	}
	function disarmGesture() {
		armed = false;
		document.removeEventListener('click', onGesture, true);
		document.removeEventListener('touchend', onGesture, true);
		document.removeEventListener('keydown', onGesture, true);
	}

	btn.addEventListener('click', function (ev) {
		ev.preventDefault();
		ev.stopPropagation();
		if (state === 'on') {
			save(false);
			disarmGesture();
			disable();
		} else {
			save(true);
			disarmGesture();
			enable();
		}
	});

	// Wake locks / video playback get dropped when the page is hidden; resume on return.
	document.addEventListener('visibilitychange', function () {
		if (document.visibilityState !== 'visible' || !load()) return;
		enable();
	});

	if (load()) {
		state = 'pending';
		armGesture();
	}
	render();
})();
