// SPDX-License-Identifier: MIT

// MIT License

// Copyright (c) 2026 Ericsson

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

const assert = require('assert');
const fs = require('fs');
const vscode = require('vscode');

const {
	resolvePlantUmlJarPath,
	PlantUmlConfigError,
	SHARED_DEFAULT_JAR_PATH
} = require('../src/plantumlRenderer');

const CONFIG_SECTION = 'plantumlInteractive';
const CONFIG_KEY = 'plantumlJar';

/**
 * Set the plantumlInteractive.plantumlJar setting for the duration of a
 * test and restore it afterwards.
 *
 * @param {string|undefined} value
 * @returns {Promise<() => Promise<void>>} a restore function
 */
async function setJarSetting(value) {
	const config = vscode.workspace.getConfiguration(CONFIG_SECTION);
	await config.update(CONFIG_KEY, value, vscode.ConfigurationTarget.Global);
	return async () => {
		await config.update(CONFIG_KEY, undefined, vscode.ConfigurationTarget.Global);
	};
}

suite('resolvePlantUmlJarPath', () => {
	let originalExistsSync;
	let originalEnvJar;

	setup(() => {
		originalExistsSync = fs.existsSync;
		originalEnvJar = process.env.PLANTUML_JAR;
		delete process.env.PLANTUML_JAR;
	});

	teardown(() => {
		fs.existsSync = originalExistsSync;
		if (originalEnvJar === undefined) {
			delete process.env.PLANTUML_JAR;
		} else {
			process.env.PLANTUML_JAR = originalEnvJar;
		}
	});

	test('setting takes precedence over the shared default path', async () => {
		const settingPath = '/configured/plantuml.jar';
		fs.existsSync = (p) => p === settingPath || p === SHARED_DEFAULT_JAR_PATH;

		const restore = await setJarSetting(settingPath);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), settingPath);
		} finally {
			await restore();
		}
	});

	test('env var takes precedence over the shared default path', async () => {
		const envPath = '/env/plantuml.jar';
		fs.existsSync = (p) => p === envPath || p === SHARED_DEFAULT_JAR_PATH;
		process.env.PLANTUML_JAR = envPath;

		const restore = await setJarSetting(undefined);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), envPath);
		} finally {
			await restore();
		}
	});

	test('shared default path is used when nothing else is configured and it exists', async () => {
		fs.existsSync = (p) => p === SHARED_DEFAULT_JAR_PATH;

		const restore = await setJarSetting(undefined);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), SHARED_DEFAULT_JAR_PATH);
		} finally {
			await restore();
		}
	});

	test('throws when nothing is configured and the shared default path does not exist', async () => {
		fs.existsSync = () => false;

		const restore = await setJarSetting(undefined);
		try {
			assert.throws(() => resolvePlantUmlJarPath(), PlantUmlConfigError);
		} finally {
			await restore();
		}
	});

	test('shared default path is used when the setting is explicitly set to that same path and it exists', async () => {
		fs.existsSync = (p) => p === SHARED_DEFAULT_JAR_PATH;

		const restore = await setJarSetting(SHARED_DEFAULT_JAR_PATH);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), SHARED_DEFAULT_JAR_PATH);
		} finally {
			await restore();
		}
	});
});
