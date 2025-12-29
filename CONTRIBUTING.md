# Contributing to PySol FC

You want to contribute? That's great! Welcome aboard.  Before submitting issues or PRs, please read the details below to make sure your contributions can be reviewed smoothly.  First of all see [these links](https://github.com/shlomif/Freenode-programming-channel-FAQ/blob/master/FAQ.mdwn#i-want-to-contribute-to-an-open-source-project-but-how-which-one-can-i-contribute-to)
for general guidelines for contributing to open source.

# Project Scope and Philosophy

PySolFC is a collection of single player solitaire and puzzle games, focused on maintaining a high-quality library of popular and unique games.

The goal is not to include every possible minor variant of each major game.  While minor variants are allowed and very often added, we avoid bulk-adding games that differ only in trivial ways purely to inflate the game count.  Instead, the project aims to maintain a curated selection of high-quality games with a consistent style and user experience.

Contributions are always welcome, including items that are not currently on the primary developers' roadmap.  However, all changes are reviewed with respect to quality, scope, potential maintenance cost, and impact on existing user experience.  Some features may be considered impractical given the current architecture or available resources.  This does not mean they are forbidden, but they will be reviewed with additional scrutiny to ensure long-term quality and maintainability.

Because they require fundamentally different design considerations and features, multiplayer games are considered out of scope for this project.

# Contribution constraints

- The [GitHub Actions CI build](https://github.com/shlomif/PySolFC/actions) and [AppVeyor build](https://ci.appveyor.com/project/shlomif/pysolfc) (which also run the test suite) should pass on each commit.
- Your contributions should be under [GPLv3+](https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3) or a [compatible free software licence](https://www.gnu.org/licenses/license-list.html#GPLCompatibleLicenses), but please don't put them under the [AGPL](https://en.wikipedia.org/wiki/Affero_General_Public_License), which adds additional restrictions.
- The code should be compatible with Python 3.7 and above.
- Changes should not remove, replace, or override existing features, without a clear, well-documented justification.

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

Display improvements are welcome, but can be subjective.  Changes that affect the visual layout or presentation of the games should be introduced as an optional, toggleable settings where possible. 

## Adding new games

First of all there is the "Solitaire Wizard" which may be used to generate many
custom variants. It lives in the Edit menu.

Otherwise, the games' sources live under
[the pysollib/games/](pysollib/games/) directory in the repository, and are
written in Python 3.x and you can try inheriting from an existing
variant [class](https://en.wikipedia.org/wiki/Class_%28computer_programming%29).

Contributions adding new games should align with the project scope and design philosophy described above.  While minor game variants are acceptable, not every possible variant is required.  Creating new cardset types is a major change, and should be reserved for major releases.

In addition to adding the game's source code, be sure to add the game's metadata.  At minimum, you should:
- In html-src/rules, create a rules file for the game in question.  Use an existing rules file as a guideline.  Ideally, each set of game rules should be written in such a way that a non-PySol user can read the rules and know how to play the game with their own deck of cards.  For games that are only slightly different from other games, referencing the more common variant's rules is okay.
- In the pysollib/gamedb.py file, update the GAMES_BY_PYSOL_VERSION dictionary to include the new game's ID for the "dev" key.  If the "dev" entry does not exist, add it.
- If you know the inventor for the game, update the inventor's entry in the GAMES_BY_INVENTORS dictionary in the same file.

## Contributing changesets / patches / diffs

One can contribute changesets either by opening [pull-requests](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/creating-an-issue-or-pull-request) or merge requests,
or by submitting patches generated by [git diff](https://git-scm.com/docs/git-diff) or [git format-patch](https://git-scm.com/docs/git-format-patch)
to a developer's email (e.g [@shlomif's](https://www.shlomifish.org/me/contact-me/) ) or uploading it to a web service (e.g: a pastesite, dropbox,
or Google Drive).

If the contribution resolves a particular issue, you can identify this by adding the issue number to the end of the commit description in parenthesis.

Note that larger or higher risk changes may require additional discussion or refinement before they are accepted.

## Review guidelines

Pull requests and patches will be reviewed with the following in mind:
- Quality and polish matter.  Features should be complete, and feel like a natural, integrated part of the application.
- Existing features should not be removed or replaced without clear justification.  In general, improvements should extend or supplement existing features rather than override it.
- User-visible display changes should be implemented as toggleable options whenever it is feasible and reasonable to do so.
- Features should be tested in a variety of scenarios.  While testing every game is not required, changes should be validated against a representative range of different games and layouts, not just ideal or limited cases.
- Maintenance cost is a factor.  Features that significantly increase complexity or introduce unnecessary long-term maintenance burden may be rejected or require revision.
- Ideas considered impractical may still be accepted if they are implemented cleanly and correctly, though they will be reviewed with additional scrutiny due to their inherent risk.
- Larger or higher-risk changes may require additional discussion, testing, or refinement before being merged, and may be deferred to a future (major) release.

# The Release Process

Before publishing a release, please open an issue in GitHub, indicating your intent to do so, to confirm with any other developers if they have any objections, or any WIP features/tickets that should be included in the upcoming release.  It's best to do this a week or two before you plan to actually publish the release.  No responses on this for a couple weeks can be considered approval to proceed.  Releases tagged without verifying with other developers may be removed.

In order to publish a new version, follow these steps:

1. Update `NEWS.asciidoc`.  The release notes should also be added to `html-src/news.html`, along with `templates/index.html` in the website repo.
2. Update the `VERSION_TUPLE =` line in `pysollib/settings.py`.
3. Check the `GAMES_BY_PYSOL_VERSION` dictionary in the `pysollib/gamedb.py` file.  If there's a "dev" entry in this dictionary, change that entry's key to be the new version number.  If there isn't a "dev" entry, ignore this step.
4. Test using `gmake test` .
5. `git commit` the changes .
6. `git tag pysolfc-2.6.5` (or equivalent version).
7. `git push` and `git push --tags` to https://github.com/shlomif/PySolFC .
8. Wait for the AppVeyor build for the tag to complete and scan the .exe using https://www.virustotal.com/ .
9. Grab the macOS installer (.dmg) from [GitHub Actions](https://github.com/shlomif/PySolFC/actions/workflows/macos-package.yml) (look for an artifact called `pysolfc-dmg`).
10. Run `gmake dist`.
11. Use [rexz9](https://github.com/shlomif/shlomif-computer-settings/blob/567b6ab3f4272ad66bf331536dc80bf58bfff3af/shlomif-settings/bash-aliases/user_aliases.bash#L57) on `dist/PySol*.tar.xz`.
12. Go to https://sourceforge.net/projects/pysolfc/files/PySolFC/ and add a folder called PySolFC-2.6.5 (note the capitalisation).
13. Add the tar.xz, the .exe and the .dmg there and mark them as defaults for the right OSes.

# Long-term, large-scale, tasks

- Support SVG cardsets.
- An optional [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) (Read-eval-print loop)
- Listen on a TCP / HTTP+REST port.
- A web-based version.
- Support a more secure saved-games format than the pickle-based-one.
