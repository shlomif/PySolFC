# Contributing to PySol FC

You want to contribute? That's great! Welcome aboard. First of all see [these links](https://github.com/shlomif/Freenode-programming-channel-FAQ/blob/master/FAQ.mdwn#i-want-to-contribute-to-an-open-source-project-but-how-which-one-can-i-contribute-to)
for general guidelines for contributing to open source.

# Contribution constraints

- The [Travis-CI build](https://travis-ci.org/shlomif/PySolFC) and [AppVeyor build](https://ci.appveyor.com/project/shlomif/pysolfc) (which also run the test suite) should pass on each commit.
- Your contributions should be under [GPLv3+](https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3) or a [compatible free software licence](https://www.gnu.org/licenses/license-list.html#GPLCompatibleLicenses), but please don't put them under the [AGPL](https://en.wikipedia.org/wiki/Affero_General_Public_License), which adds additional restrictions.
- The code should be compatible with both Python 2.7.x and Python 3.4.x-and-above.

# How you can contribute

- Translate PySol to a human language you know.
- Test the "master" branch version of the version control repository or other prereleases.
- Try to reproduce [open issues](https://github.com/shlomif/PySolFC/issues)
- Try to fix bugs.
- Add new games.
- Improve the documentation / online help
- [Refactor](https://en.wikipedia.org/wiki/Code_refactoring) the code.
- Add new features.
- Contribute graphics
- Improve the site
- Package PySol for a new package repository or OS, or update existing packages.
- Make a monetary donation.
- [Star](https://help.github.com/articles/about-stars/) or [Watch](https://help.github.com/articles/watching-and-unwatching-repositories/) the repository on GitHub

## Adding new games

First of all there is the "Solitaire Wizard" which may be used to generate many
custom variants. It lives in the Edit menu.

Otherwise, the games' sources live under
[the pysollib/games/](pysollib/games/) directory in the repository, and are
written in Python 2.7/3.x and you can try inheriting from an existing
variant [class](https://en.wikipedia.org/wiki/Class_%28computer_programming%29).

# The Release Process

In order to publish a new version, follow these steps:

1. Update `NEWS.asciidoc`.
2. Update the `VERSION_TUPLE =` line in `pysollib/settings.py`.
3. Test using `gmake test` .
4. `git commit` the changes .
5. `git tag pysolfc-2.6.5` (or equivalent version).
6. `git push` and `git push --tags` to https://github.com/shlomif/PySolFC .
7. Wait for the AppVeyor build for the tag to complete and scan the .exe using https://www.virustotal.com/ .
8. Run `gmake dist`.
9. Use [rexz9](https://github.com/shlomif/shlomif-computer-settings/blob/567b6ab3f4272ad66bf331536dc80bf58bfff3af/shlomif-settings/bash-aliases/user_aliases.bash#L57) on `dist/PySol*.tar.xz`.
10. Go to https://sourceforge.net/projects/pysolfc/files/PySolFC/ and add a folder called PySolFC-2.6.5 (note the capitalisation).
11. Add the tar.xz and the .exe there and mark them as defaults for the right OSes.
