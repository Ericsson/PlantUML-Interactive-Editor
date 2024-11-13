# Deploying a new version to https://pdupc-pcsmplantuml.sero.wh.rnd.internal.ericsson.se

1. Update README.md and FEATURES.md
2. Update `__version__` in `src/plantuml_gui/__about__.py`
3. Commit, push to Gerrit, review and submit
4. `su -l efuncpcsm`
5. Paste password and press Enter
6. `cd /proj/pdupc_webdocs/sites/pdupc-pcsmplantuml/plantuml_gui`
7. `git pull --rebase`
8  `../.venv/bin/pip install -e .`
9. `touch ../wsgi.py`
