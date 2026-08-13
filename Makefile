PIP = venv/bin/pip
PY = venv/bin/python3
FALKE = venv/bin/flake8
MYPY = venv/bin/mypy

install:
	python3 -m venv venv
	$(PIP) install pygame flake8 mypy 

run:
	$(PY) pac_man.py config.json

debug:
	$(PY) -m pdb pac-man.py config.json

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__ .mypy_cache venv

lint:
	$(FALKE) src
	$(MYPY) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs src