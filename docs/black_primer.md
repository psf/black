# black-primer

`black-primer` is a tool built for CI (and humans) to have _Black_ `--check` a number of
(configured in `primer.json`) Git accessible projects in parallel. _(A PR will be
accepted to add Mercurial support.)_

## Run flow

- Ensure we have a `black` + `git` in PATH
- Load projects from `primer.json`
- Run projects in parallel with `--worker` workers (defaults to CPU count / 2)
  - Checkout projects
  - Run black and record result
  - Clean up repository checkout _(can optionally be disabled via `--keep`)_
- Display results summary to screen
- Default to cleaning up `--work-dir` (which defaults to tempfile schemantics)
- Return
  - 0 for successful run
  - < 0 for environment / internal error
  - \> 0 for each project with an error

## Speed up runs 🏎

If you're running locally yourself to test black on lots of code try:

- Using `-k` / `--keep` + `-w` / `--work-dir` so you don't have to re-checkout the repo
  each run

## CLI arguments

```text
Usage: black-primer [OPTIONS]

  primer - prime projects for blackening... 🏴

Options:
  -c, --config PATH      JSON config file path  [default: /Users/cooper/repos/
                         black/src/black_primer/primer.json]

  --debug                Turn on debug logging  [default: False]
  -k, --keep             Keep workdir + repos post run  [default: False]
  -L, --long-checkouts   Pull big projects to test  [default: False]
  -R, --rebase           Rebase project if already checked out  [default:
                         False]

  -w, --workdir PATH     Directory path for repo checkouts  [default: /var/fol
                         ders/tc/hbwxh76j1hn6gqjd2n2sjn4j9k1glp/T/primer.20200
                         517125229]

  -W, --workers INTEGER  Number of parallel worker coroutines  [default: 2]
  -h, --help             Show this message and exit.
```

## Primer config file

The config file is in JSON format. Its main element is the `"projects"` dictionary and
each parameter is explained below:

```json
{
  "projects": {
    "00_Example": {
      "cli_arguments": "List of extra CLI arguments to pass Black for this project",
      "expect_formatting_changes": "Boolean to indicate that the version of Black is expected to cause changes",
      "git_clone_url": "URL you would pass `git clone` to check out this repo",
      "long_checkout": "Boolean to have repo skipped by default unless `--long-checkouts` is specified",
      "py_versions": "List of major Python versions to run this project with - all will do as you'd expect - run on ALL versions"
    },
    "aioexabgp": {
      "cli_arguments": [],
      "expect_formatting_changes": true,
      "git_clone_url": "https://github.com/cooperlees/aioexabgp.git",
      "long_checkout": false,
      "py_versions": ["all", "3.8"]
    }
  }
}
```

An example primer config file is used by Black
[here](https://github.com/psf/black/blob/master/src/black_primer/primer.json)

## Example run

```console
cooper-mbp:black cooper$ ~/venvs/b/bin/black-primer
[2020-05-17 13:06:40,830] INFO: 4 projects to run Black over (lib.py:270)
[2020-05-17 13:06:44,215] INFO: Analyzing results (lib.py:285)
-- primer results 📊 --

3 / 4 succeeded (75.0%) ✅
1 / 4 FAILED (25.0%) 💩
 - 0 projects disabled by config
 - 0 projects skipped due to Python version
 - 0 skipped due to long checkout

Failed projects:

## flake8-bugbear:
 - Returned 1
 - stdout:
--- tests/b303_b304.py	2020-05-17 20:04:09.991227 +0000
+++ tests/b303_b304.py	2020-05-17 20:06:42.753851 +0000
@@ -26,11 +26,11 @@
     maxint = 5  # this is okay
     # the following should not crash
     (a, b, c) = list(range(3))
     # it is different than this
     a, b, c = list(range(3))
-    a, b, c, = list(range(3))
+    a, b, c = list(range(3))
     # and different than this
     (a, b), c = list(range(3))
     a, *b, c = [1, 2, 3, 4, 5]
     b[1:3] = [0, 0]

would reformat tests/b303_b304.py
Oh no! 💥 💔 💥
1 file would be reformatted, 22 files would be left unchanged.
```
