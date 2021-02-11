# Makefile for PySolFC

ifeq ($(OS),Windows_NT)
	path_sep = ;
else
	path_sep = :
endif
export PYTHONPATH := $(PYTHONPATH)$(path_sep)$(CURDIR)

.PHONY: all install dist rpm all_games_html rules pot mo pretest test runtest

all:
	@echo "No default target"

install:
	python3 setup.py install

dist: all_games_html rules mo
	python3 setup.py sdist

rpm: all_games_html rules mo
	python3 setup.py bdist_rpm

DOCS_DIR = docs
HTML_DIR = data/html
ALL_GAMES_HTML_BASE = all_games.html
ALL_GAMES_HTML = $(HTML_DIR)/$(ALL_GAMES_HTML_BASE)
ALL_GAMES_HTML__FOR_WEBSITE = $(DOCS_DIR)/$(ALL_GAMES_HTML_BASE)
all_games_html: $(ALL_GAMES_HTML)

$(ALL_GAMES_HTML) $(ALL_GAMES_HTML__FOR_WEBSITE): rules
	cd $(HTML_DIR) && $(CURDIR)/scripts/all_games.py html id rules > $(ALL_GAMES_HTML_BASE)
	./scripts/all_games.py html id doc/rules bare > $(ALL_GAMES_HTML__FOR_WEBSITE)

rules:
	cd html-src && ./gen-html.py
	cp -r html-src/images html-src/html
	rm -rf data/html
	mv html-src/html data

pot:
	./scripts/all_games.py gettext > po/games.pot
	xgettext --keyword=n_ --add-comments=TRANSLATORS: -o po/pysol.pot \
		pysollib/*.py pysollib/*/*.py pysollib/*/*/*.py data/pysolfc.glade
	set -e; \
	for lng in de fr pl it ru ; do \
		msgmerge --update --quiet --backup=none po/$${lng}_pysol.po po/pysol.pot; \
		msgmerge --update --quiet --backup=none po/$${lng}_games.po po/games.pot; \
	done

mo:
	set -e; \
	for lang in ru de pl it; do \
		mkdir -p locale/$${lang}/LC_MESSAGES; \
		msgcat --use-first po/$${lang}_games.po po/$${lang}_pysol.po > po/$${lang}.po; \
		msgfmt --check -o locale/$${lang}/LC_MESSAGES/pysol.mo po/$${lang}.po; \
	done

pretest:
	rm -f tests/individually-importing/*.py tests/unit-generated/*.py # To avoid stray files
	python3 scripts/gen_individual_importing_tests.py

TEST_ENV_PATH = $(CURDIR)$(path_sep)$(CURDIR)/tests/lib
TEST_FILES = tests/style/*.t tests/t/*.py tests/individually-importing/*.py

test runtest: export PERL5LIB := $(PERL5LIB)$(path_sep)$(TEST_ENV_PATH)

test: pretest
	prove $(TEST_FILES)

runtest: pretest
	runprove $(TEST_FILES)
