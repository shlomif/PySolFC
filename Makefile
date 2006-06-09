# Makefile for PySolFC

override LANG=C

PYSOLLIB_FILES=pysollib/tk/*.py pysollib/*.py \
	pysollib/games/*.py pysollib/games/special/*.py \
	pysollib/games/contrib/*.py pysollib/games/ultra/*.py \
	pysollib/games/mahjongg/*.py

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
	(cd data/html-src && ./gen-html.py)
	cp -r data/html-src/images data/html-src/html
	rm -rf data/html
	mv data/html-src/html data

pot:
	pygettext.py -k n_ -o po/pysol.pot $(PYSOLLIB_FILES)
	./scripts/all_games.py gettext > po/games.pot
	for lng in ru; do \
		mv -f po/$${lng}_pysol.po po/$${lng}_pysol.old.po; \
		msgmerge po/$${lng}_pysol.old.po po/pysol.pot > po/$${lng}_pysol.po; \
		rm -f po/$${lng}_pysol.old.po; \
		mv -f po/$${lng}_games.po po/$${lng}_games.old.po; \
		msgmerge po/$${lng}_games.old.po po/games.pot > po/$${lng}_games.po; \
		rm -f po/$${lng}_games.old.po; \
	done

mo:
	test -d locale/ru/LC_MESSAGES || mkdir -p locale/ru/LC_MESSAGES
	test -d locale/ru_RU/LC_MESSAGES || mkdir -p locale/ru_RU/LC_MESSAGES
	msgcat po/ru_games.po po/ru_pysol.po > po/ru.po 2>/dev/null
	msgfmt -o locale/ru/LC_MESSAGES/pysol.mo po/ru.po
	cp -f locale/ru/LC_MESSAGES/pysol.mo locale/ru_RU/LC_MESSAGES/pysol.mo
