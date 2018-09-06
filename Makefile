# Makefile for PySolFC

override LANG=C
override PYSOL_DEBUG=1

PYSOLLIB_FILES=pysollib/tk/*.py pysollib/tile/*.py pysollib/*.py \
	pysollib/games/*.py pysollib/games/special/*.py \
	pysollib/games/ultra/*.py pysollib/games/mahjongg/*.py \
	pysollib/kivy/*.py

.PHONY : all install dist all_games_html rules pot mo

all:
	@echo "No default target"

install:
	python setup.py install

dist: all_games_html rules mo
	python3 setup.py sdist

rpm: all_games_html rules mo
	python setup.py bdist_rpm

all_games_html:
	PYTHONPATH=`pwd` ./scripts/all_games.py html id doc/rules bare > docs/all_games.html

rules:
	export PYTHONPATH=`pwd`; (cd html-src && ./gen-html.py)
	cp -r html-src/images html-src/html
	rm -rf data/html
	mv html-src/html data

pot:
	PYTHONPATH=`pwd` ./scripts/all_games.py gettext > po/games.pot
	PYTHONPATH=`pwd` ./scripts/pygettext.py -k n_ --ngettext-keyword ungettext -o po/pysol-1.pot $(PYSOLLIB_FILES)
	xgettext -L C --keyword=N_ -o po/pysol-2.pot data/glade-translations
	msgcat po/pysol-1.pot po/pysol-2.pot > po/pysol.pot
	rm -f po/pysol-1.pot po/pysol-2.pot
	for lng in ru pl; do \
		mv -f po/$${lng}_pysol.po po/$${lng}_pysol.old.po; \
		msgmerge po/$${lng}_pysol.old.po po/pysol.pot > po/$${lng}_pysol.po; \
		rm -f po/$${lng}_pysol.old.po; \
		mv -f po/$${lng}_games.po po/$${lng}_games.old.po; \
		msgmerge po/$${lng}_games.old.po po/games.pot > po/$${lng}_games.po; \
		rm -f po/$${lng}_games.old.po; \
	done

mo:
	for loc in ru ru_RU de de_AT de_BE de_DE de_LU de_CH pl pl_PL it it_IT; do \
		test -d locale/$${loc}/LC_MESSAGES || mkdir -p locale/$${loc}/LC_MESSAGES; \
	done
	for lang in ru pl it; do \
		msgcat --use-first po/$${lang}_games.po po/$${lang}_pysol.po > po/$${lang}.po 2>/dev/null; \
	done
	for lang in ru de pl it; do \
		msgfmt -o locale/$${lang}/LC_MESSAGES/pysol.mo po/$${lang}.po; \
	done
	cp -f locale/ru/LC_MESSAGES/pysol.mo locale/ru_RU/LC_MESSAGES/pysol.mo
	for dir in de_AT de_BE de_DE de_LU de_CH; do \
		cp -f locale/de/LC_MESSAGES/pysol.mo locale/$${dir}/LC_MESSAGES/pysol.mo; \
	done
	cp -f locale/pl/LC_MESSAGES/pysol.mo locale/pl_PL/LC_MESSAGES/pysol.mo
	cp -f locale/it/LC_MESSAGES/pysol.mo locale/it_IT/LC_MESSAGES/pysol.mo

pretest:
	@rm -f tests/individually-importing/*.py # To avoid stray files
	python scripts/gen_individual_importing_tests.py

TEST_ENV_PATH = "`pwd`:`pwd`/tests/lib"
TEST_ENV = PYTHONPATH=$(TEST_ENV_PATH) PERL5LIB=$(TEST_ENV_PATH)
TEST_FILES = tests/style/*.t tests/unit-generated/*.py tests/individually-importing/*.py

define RUN_TESTS
$(TEST_ENV) $1 $(TEST_FILES)
endef

test: pretest
	$(call RUN_TESTS,prove)

runtest: pretest
	$(call RUN_TESTS,runprove)
