PIP = venv/bin/pip
PY = venv/bin/python3
PK = venv/bin/pyinstaller
FALKE = venv/bin/flake8
MYPY = venv/bin/mypy

install:
	python3 -m venv venv
	$(PIP) install -r requirements

run:
	$(PY) pac-man.py config.json

debug:
	$(PY) -m pdb pac-man.py config.json

package:
	$(PK) --onedir --name PacMan --icon="assets/icon.ico" \
			--add-data "assets:assets" \
			--add-data "src/config/default_conf.json:src/config" \
			pac-man.py
	cp src/INSTRUCTIONS.txt dist

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__ .mypy_cache venv

lint:
	$(FALKE) src
	$(MYPY) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs src