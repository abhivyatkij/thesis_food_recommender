.PHONY: clean_output clean_logs clean_all

VENV_NAME?=venv1
env = venv/bin/activate
python = . $(env); LC_CTYPE=C.UTF-8 python

# tools
mkdir = $(python) tools/mkdir.py
# since clean needs this, and the virtual env might not exist, we ignore the env here
rm = python tools/rm.py

$(env): requirements.txt
	$(rm) venv/
	python -m pip install --user virtualenv
	python -m virtualenv -p python3 venv
	$(python) -m pip install -r requirements.txt
	$(python) -m pip install -e .

in: $(env)
	$(mkdir) application/in/

out: $(env)
	$(mkdir) application/out/

logs: $(env)
	$(mkdir) application/logs/

clean_output:
	$(rm) application/in/food_words_vocabulary.csv
	$(rm) application/out/

clean_logs:
	$(rm) application/logs/

clean_all: clean_output clean_logs
	$(rm) venv/