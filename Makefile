# Makefile for PySolFC

export PYTHONPATH := $(PYTHONPATH):$(CURDIR)

PYSOLLIB_FILES = pysollib/tk/*.py pysollib/tile/*.py pysollib/*.py \
	pysollib/games/*.py pysollib/games/special/*.py \
	pysollib/games/ultra/*.py pysollib/games/mahjongg/*.py \
	pysollib/kivy/*.py

.PHONY: all install dist rpm all_games_html rules pot mo pretest test runtest

all:
	@echo "No default target"

install:
	python3 setup.py install

dist: all_games_html rules mo
	python3 setup.py sdist

rpm: all_games_html rules mo
	python3 setup.py bdist_rpm

all_games_html: rules
	cd data/html && $(CURDIR)/scripts/all_games.py html id rules > all_games.html

rules:
	cd html-src && ./gen-html.py
	cp -r html-src/images html-src/html
	rm -rf data/html
	mv html-src/html data

pot:
	./scripts/all_games.py gettext > po/games.pot
	./scripts/pygettext.py -k n_ --ngettext-keyword ungettext -o po/pysol-1.pot $(PYSOLLIB_FILES)
	xgettext -L C --keyword=N_ -o po/pysol-2.pot data/glade-translations
	msgcat po/pysol-1.pot po/pysol-2.pot > po/pysol.pot
	rm -f po/pysol-1.pot po/pysol-2.pot
	set -e; \
	for lng in ru de pl it; do \
		msgmerge --update --quiet --backup=none po/$${lng}_pysol.po po/pysol.pot; \
		msgmerge --update --quiet --backup=none po/$${lng}_games.po po/games.pot; \
	done

mo:
	set -e; \
	for lang in ru de pl it; do \
		mkdir -p locale/$${lang}/LC_MESSAGES; \
		msgcat --use-first po/$${lang}_games.po po/$${lang}_pysol.po > po/$${lang}.po; \
		msgfmt -o locale/$${lang}/LC_MESSAGES/pysol.mo po/$${lang}.po; \
	done

pretest:
	rm -f tests/individually-importing/*.py # To avoid stray files
	python3 scripts/gen_individual_importing_tests.py

TEST_ENV_PATH = $(CURDIR):$(CURDIR)/tests/lib
TEST_FILES = tests/style/*.t tests/unit-generated/*.py tests/individually-importing/*.py

test runtest: export PYTHONPATH := $(PYTHONPATH):$(TEST_ENV_PATH)
test runtest: export PERL5LIB := $(PERL5LIB):$(TEST_ENV_PATH)

test: pretest
	prove $(TEST_FILES)

runtest: pretest
	runprove $(TEST_FILES)
