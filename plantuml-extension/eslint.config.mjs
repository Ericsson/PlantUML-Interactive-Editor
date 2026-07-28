import globals from "globals";

const rules = {
    "no-const-assign": "warn",
    "no-this-before-super": "warn",
    "no-undef": "warn",
    "no-unreachable": "warn",
    "no-unused-vars": "warn",
    "constructor-super": "warn",
    "valid-typeof": "warn",
};

export default [{
    ignores: [
        // The downloaded VS Code build for `npm test` lands here and ships its
        // own eslint configs, which crash this run. Flat config does not read
        // .gitignore, so it has to be excluded explicitly or `npm test` breaks
        // (pretest runs lint) as soon as the test harness has been used once.
        ".vscode-test/**",
        // Mirrored from src/plantuml_gui/static by scripts/sync_assets.py, and
        // third-party libraries. Linting a copy reports problems in a file
        // nobody edits here; the originals live in the Python package.
        "media/app/**",
        "media/vendor/**",
    ],
}, {
    // Extension host: Node.
    files: ["**/*.js"],
    ignores: ["media/**"],
    languageOptions: {
        globals: {
            ...globals.commonjs,
            ...globals.node,
            ...globals.mocha,
        },
        ecmaVersion: 2022,
        sourceType: "module",
    },
    rules,
}, {
    // Hand-written webview scripts: browser, plus the globals they get from the
    // VS Code webview API and from the mirrored app scripts loaded alongside.
    files: ["media/*.js"],
    languageOptions: {
        globals: {
            ...globals.browser,
            acquireVsCodeApi: "readonly",
            // Declared by media/app/script.js (`let editor`) and assigned by
            // media/webviewInit.js -- see the load-order note there.
            editor: "writable",
            renderPlantUml: "readonly",
            debouncedRenderPlantUml: "readonly",
            clearMarkers: "readonly",
            cursorChangeListener: "readonly",
            initEditorHoverHighlighting: "readonly",
            titleEventListeners: "readonly",
            panzoom: "readonly",
        },
        ecmaVersion: 2022,
        sourceType: "script",
    },
    rules,
}];
