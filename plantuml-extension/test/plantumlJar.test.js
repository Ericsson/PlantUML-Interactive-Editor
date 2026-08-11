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

const settings = require('../src/settings');
const {
	resolvePlantUmlJarPath,
	PlantUmlConfigError,
	JAR_KEY,
	JAR_SETTING,
	JAR_ENV,
	SHARED_JAR_PATH
} = require('../src/plantumlJar');

/**
 * Make `paths` the only files on disk, for the duration of a test.
 *
 * statSync rather than existsSync because "is a file" is the check that
 * matters: a directory named plantuml.jar passes existence and then fails
 * inside java.
 *
 * @param {string[]} paths
 * @param {string[]} [directories] paths that exist but are not files
 * @returns {() => void} a restore function
 */
function stubFilesystem(paths, directories = []) {
	const original = fs.statSync;

	fs.statSync = (candidate) => {
		if (paths.includes(candidate)) {
			return { isFile: () => true };
		}
		if (directories.includes(candidate)) {
			return { isFile: () => false };
		}
		const err = new Error(`ENOENT: ${candidate}`);
		err.code = 'ENOENT';
		throw err;
	};

	return () => {
		fs.statSync = original;
	};
}

/**
 * Set the jar setting for the duration of a test and restore it afterwards.
 *
 * @param {string|undefined} value
 * @returns {Promise<() => Promise<void>>} a restore function
 */
async function setJarSetting(value) {
	const target = vscode.workspace.getConfiguration(settings.SECTION);
	await target.update(JAR_KEY, value, vscode.ConfigurationTarget.Global);
	return async () => {
		await target.update(JAR_KEY, undefined, vscode.ConfigurationTarget.Global);
	};
}

suite('jar setting: the manifest', () => {
	test('declares an empty default', async () => {
		// `get()` returns the manifest default whenever a setting is untouched,
		// so a non-empty default here would make PLANTUML_JAR unreachable for
		// every user who never opens Settings.
		const declared =
			require('../package.json').contributes.configuration.properties[JAR_SETTING];

		assert.strictEqual(declared.default, '');
	});

	test('does not name the shared install path', () => {
		// It belongs in plantumlJar.js, where it ranks below the two explicit
		// knobs.
		const manifest = JSON.stringify(require('../package.json'));

		assert.ok(!manifest.includes(SHARED_JAR_PATH), 'manifest hardcodes the shared path');
	});
});

suite('resolvePlantUmlJarPath: precedence', () => {
	let restoreFs;
	let originalEnvJar;

	setup(() => {
		originalEnvJar = process.env[JAR_ENV];
		delete process.env[JAR_ENV];
	});

	teardown(() => {
		restoreFs?.();
		restoreFs = undefined;
		if (originalEnvJar === undefined) {
			delete process.env[JAR_ENV];
		} else {
			process.env[JAR_ENV] = originalEnvJar;
		}
	});

	test('the setting wins over the environment variable', async () => {
		const settingPath = '/configured/plantuml.jar';
		restoreFs = stubFilesystem([settingPath, '/env/plantuml.jar']);
		process.env[JAR_ENV] = '/env/plantuml.jar';

		const restore = await setJarSetting(settingPath);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), settingPath);
		} finally {
			await restore();
		}
	});

	test('the environment variable is used when the setting is untouched', async () => {
		// The untouched case matters on its own: `get()` answers with the
		// manifest default, and only an empty one lets this env var be reached.
		const envPath = '/env/plantuml.jar';
		restoreFs = stubFilesystem([envPath, SHARED_JAR_PATH]);
		process.env[JAR_ENV] = envPath;

		const restore = await setJarSetting(undefined);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), envPath);
		} finally {
			await restore();
		}
	});

	test('the environment variable is used when the setting is explicitly cleared', async () => {
		const envPath = '/env/plantuml.jar';
		restoreFs = stubFilesystem([envPath]);
		process.env[JAR_ENV] = envPath;

		const restore = await setJarSetting('');
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), envPath);
		} finally {
			await restore();
		}
	});

	test('the shared install path is used when nothing is configured', async () => {
		restoreFs = stubFilesystem([SHARED_JAR_PATH]);

		const restore = await setJarSetting(undefined);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), SHARED_JAR_PATH);
		} finally {
			await restore();
		}
	});
});

suite('resolvePlantUmlJarPath: validation', () => {
	let restoreFs;
	let originalEnvJar;

	setup(() => {
		originalEnvJar = process.env[JAR_ENV];
		delete process.env[JAR_ENV];
	});

	teardown(() => {
		restoreFs?.();
		restoreFs = undefined;
		if (originalEnvJar === undefined) {
			delete process.env[JAR_ENV];
		} else {
			process.env[JAR_ENV] = originalEnvJar;
		}
	});

	test('throws when nothing is configured and the shared path is absent', async () => {
		restoreFs = stubFilesystem([]);

		const restore = await setJarSetting(undefined);
		try {
			assert.throws(() => resolvePlantUmlJarPath(), PlantUmlConfigError);
		} finally {
			await restore();
		}
	});

	test('rejects a configured path that is a directory, not a file', async () => {
		// Matches os.path.isfile in serve.py's check_jar: a directory named
		// plantuml.jar passes an existence check and then fails inside java.
		const directory = '/configured/plantuml.jar';
		restoreFs = stubFilesystem([], [directory]);

		const restore = await setJarSetting(directory);
		try {
			assert.throws(() => resolvePlantUmlJarPath(), PlantUmlConfigError);
		} finally {
			await restore();
		}
	});

	test('a bad setting does not fall through to a working environment variable', async () => {
		// Falling through is how configuration comes to look ignored: the user
		// would see a diagram rendered by a jar they did not choose.
		restoreFs = stubFilesystem(['/env/plantuml.jar']);
		process.env[JAR_ENV] = '/env/plantuml.jar';

		const restore = await setJarSetting('/typo/plantuml.jar');
		try {
			assert.throws(() => resolvePlantUmlJarPath(), PlantUmlConfigError);
		} finally {
			await restore();
		}
	});

	test('a bad environment variable does not fall through to the shared path', async () => {
		restoreFs = stubFilesystem([SHARED_JAR_PATH]);
		process.env[JAR_ENV] = '/typo/plantuml.jar';

		const restore = await setJarSetting(undefined);
		try {
			assert.throws(() => resolvePlantUmlJarPath(), PlantUmlConfigError);
		} finally {
			await restore();
		}
	});

	test('the message names the path and the setting to fix', async () => {
		const settingPath = '/typo/plantuml.jar';
		restoreFs = stubFilesystem([]);

		const restore = await setJarSetting(settingPath);
		try {
			assert.throws(resolvePlantUmlJarPath, (err) => {
				assert.ok(err.message.includes(settingPath), err.message);
				assert.ok(err.message.includes(JAR_SETTING), err.message);
				return true;
			});
		} finally {
			await restore();
		}
	});

	test('the message names the environment variable when that is the bad source', async () => {
		restoreFs = stubFilesystem([]);
		process.env[JAR_ENV] = '/typo/plantuml.jar';

		const restore = await setJarSetting(undefined);
		try {
			assert.throws(resolvePlantUmlJarPath, (err) => {
				assert.ok(err.message.includes(JAR_ENV), err.message);
				return true;
			});
		} finally {
			await restore();
		}
	});

	test('the unconfigured message names both knobs and the shared path', async () => {
		restoreFs = stubFilesystem([]);

		const restore = await setJarSetting(undefined);
		try {
			assert.throws(resolvePlantUmlJarPath, (err) => {
				assert.ok(err.message.includes(JAR_SETTING), err.message);
				assert.ok(err.message.includes(JAR_ENV), err.message);
				assert.ok(err.message.includes(SHARED_JAR_PATH), err.message);
				return true;
			});
		} finally {
			await restore();
		}
	});
});

suite('resolvePlantUmlJarPath: normalization', () => {
	let restoreFs;

	teardown(() => {
		restoreFs?.();
		restoreFs = undefined;
	});

	test('a quoted, padded setting value resolves', async () => {
		// What lands in settings.json when a path is pasted out of a shell.
		const jarPath = '/opt/plantuml/plantuml.jar';
		restoreFs = stubFilesystem([jarPath]);

		const restore = await setJarSetting(`  "${jarPath}"  `);
		try {
			assert.strictEqual(resolvePlantUmlJarPath(), jarPath);
		} finally {
			await restore();
		}
	});
});
