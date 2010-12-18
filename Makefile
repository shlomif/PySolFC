# Makefile for PySolFC

override LANG=C
override PYSOL_DEBUG=1

PYSOLLIB_FILES=pysollib/tk/*.py pysollib/tile/*.py pysollib/*.py \
	pysollib/games/*.py pysollib/games/special/*.py \
	pysollib/games/ultra/*.py pysollib/games/mahjongg/*.py

.PHONY : install dist all_games_html rules pot mo

install:
	python setup.py install

dist: all_games_html rules mo
	python setup.py sdist

rpm: all_games_html rules mo
	python setup.py bdist_rpm

all_games_html:
	./scripts/all_games.py > docs/all_games.html

rules:
	(cd html-src && ./gen-html.py)
	cp -r html-src/images html-src/html
	rm -rf data/html
	mv html-src/html data

pot:
	./scripts/all_games.py gettext > po/games.pot
	./scripts/pygettext.py -k n_ --ngettext-keyword ungettext -o po/pysol-1.pot $(PYSOLLIB_FILES)
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
	for loc in ru ru_RU de de_AT de_BE de_DE de_LU de_CH pl pl_PL; do \
		test -d locale/$${loc}/LC_MESSAGES || mkdir -p locale/$${loc}/LC_MESSAGES; \
	done
	for lang in ru pl; do \
		msgcat po/$${lang}_games.po po/$${lang}_pysol.po > po/$${lang}.po 2>/dev/null; \
	done
	for lang in ru de pl; do \
		msgfmt -o locale/$${lang}/LC_MESSAGES/pysol.mo po/$${lang}.po; \
	done
	cp -f locale/ru/LC_MESSAGES/pysol.mo locale/ru_RU/LC_MESSAGES/pysol.mo
	for dir in de_AT de_BE de_DE de_LU de_CH; do \
		cp -f locale/de/LC_MESSAGES/pysol.mo locale/$${dir}/LC_MESSAGES/pysol.mo; \
	done
	cp -f locale/pl/LC_MESSAGES/pysol.mo locale/pl_PL/LC_MESSAGES/pysol.mo
