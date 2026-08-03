import globals from "globals";

export default [{
    // Both are downloaded, not written here: .vscode-test holds a whole copy
    // of VS Code, whose bundled extensions ship eslint configs of their own
    // that ESLint tries to load and fails on.
    ignores: [".vscode-test/**", "node_modules/**"],
}, {
    files: ["**/*.js"],
    languageOptions: {
        globals: {
            ...globals.commonjs,
            ...globals.node,
            ...globals.mocha,
        },

        ecmaVersion: 2022,
        sourceType: "module",
    },

    rules: {
        "no-const-assign": "warn",
        "no-this-before-super": "warn",
        "no-undef": "warn",
        "no-unreachable": "warn",
        "no-unused-vars": "warn",
        "constructor-super": "warn",
        "valid-typeof": "warn",
    },
}];
