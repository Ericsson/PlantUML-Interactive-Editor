// Runs scripts/sync_assets.py with whichever Python is actually available.
//
// `python` is not on PATH everywhere -- notably on Windows with a uv- or
// venv-managed interpreter, where the bare name resolves to nothing (or to the
// Microsoft Store stub). Hardcoding it in the npm script makes the sync
// workflow unusable for exactly the people most likely to need it.
//
// Resolution order mirrors src/sidecar.js, so configuring PLANTUML_GUI_PYTHON
// once serves both.

import { spawnSync } from 'child_process';
import { existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const scriptsDir = dirname(fileURLToPath(import.meta.url));
const extensionDir = dirname(scriptsDir);
const repoRoot = dirname(extensionDir);

const venvPython =
	process.platform === 'win32'
		? join(repoRoot, '.venv', 'Scripts', 'python.exe')
		: join(repoRoot, '.venv', 'bin', 'python');

const candidates = [
	process.env.PLANTUML_GUI_PYTHON,
	existsSync(venvPython) ? venvPython : undefined,
	process.platform === 'win32' ? 'python' : 'python3',
	'python'
].filter(Boolean);

const target = join(scriptsDir, 'sync_assets.py');
const args = process.argv.slice(2);

for (const python of candidates) {
	const result = spawnSync(python, [target, ...args], { stdio: 'inherit' });

	// ENOENT means this candidate does not exist; anything else is the script
	// itself talking, so pass its status straight through.
	if (result.error?.code === 'ENOENT') {
		continue;
	}
	if (result.error) {
		console.error(`Failed to run ${python}: ${result.error.message}`);
		process.exit(1);
	}
	process.exit(result.status ?? 1);
}

console.error(
	'No usable Python interpreter found. Tried:\n' +
		candidates.map((c) => `  ${c}`).join('\n') +
		'\n\nSet PLANTUML_GUI_PYTHON to an interpreter that has jinja2 installed.'
);
process.exit(1);
