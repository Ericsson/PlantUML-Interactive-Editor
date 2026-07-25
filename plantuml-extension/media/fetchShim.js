// Points the reused app code's relative fetch() calls at the sidecar.
//
// The web app calls fetch("editText", ...), fetch("render", ...) and so on with
// relative URLs, which in a browser resolve against the Flask origin. In a
// webview the page URL has a vscode-webview-ish origin, so they would resolve
// to nonsense. Rewriting them here is the only change those ~150 call sites
// need -- which is why this is a shim and not a refactor.
//
// Must load before any app script.
//
// Note that this makes every request cross-origin, and the token header below
// is not CORS-safelisted, so the sidecar has to answer preflights. See
// install_cors in src/plantuml_gui/serve.py.

(function () {
	const nativeFetch = window.fetch.bind(window);
	const base = window.__PLANTUML_API__;
	const token = window.__PLANTUML_TOKEN__;

	window.fetch = function (url, options = {}) {
		const target = String(url);
		const absolute = /^[a-z]+:\/\//i.test(target)
			? target
			: base + target.replace(/^\//, '');

		return nativeFetch(absolute, {
			...options,
			headers: { ...(options.headers || {}), 'X-PlantUML-Token': token }
		});
	};
})();
