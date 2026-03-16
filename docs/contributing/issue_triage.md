# Issue triage

Currently, _Black_ uses the issue tracker for bugs, feature requests, proposed style
modifications, and general user support. Each of these issues have to be triaged so they
can be eventually be resolved somehow. This document outlines the triaging process and
also the current guidelines and recommendations.

```{tip}
If you're looking for a way to contribute without submitting patches, this might be the
area for you. Since _Black_ is a popular project, its issue tracker is quite busy and
always needs more attention than is available. While triage isn't the most glamorous or
technically challenging form of contribution, it's still important. For example, we
would love to know whether that old bug report is still reproducible!

You can get easily started by reading over this document and then responding to issues.

If you contribute enough and have stayed for long enough, you may even be given
Triage permissions!
```

## The basics

_Black_ gets a whole bunch of different issues, they range from bug reports to user
support issues. To triage is to identify, organize, and kickstart the issue's journey
through its lifecycle to resolution.

More specifically, to triage an issue means to:

- identify what type and categories the issue falls under
- confirm bugs
- ask questions / for further information if necessary
- link related issues
- provide the first initial feedback / support

Note that triage is typically the first response to an issue, so don't fret if the issue
doesn't make much progress after initial triage. The main goal of triaging to prepare
the issue for future more specific development or discussion, so _eventually_ it will be
resolved.

The lifecycle of a bug report or user support issue typically goes something like this:

1. _the issue is waiting for triage_
2. **identified** - has been marked with a type label and other relevant labels, more
   details or a functional reproduction may be still needed (and therefore should be
   marked with `S: needs repro` or `S: awaiting response`)
3. **confirmed** - the issue can reproduced and necessary details have been provided
4. **discussion** - initial triage has been done and now the general details on how the
   issue should be best resolved are being hashed out
5. **awaiting fix** - no further discussion on the issue is necessary and a resolving PR
   is the next step
6. **closed** - the issue has been resolved, reasons include:
   - the issue couldn't be reproduced
   - the issue has been fixed
   - duplicate of another pre-existing issue or is invalid

For enhancement, documentation, and style issues, the lifecycle looks very similar but
the details are different:

1. _the issue is waiting for triage_
2. **identified** - has been marked with a type label and other relevant labels
3. **discussion** - the merits of the suggested changes are currently being discussed, a
   PR would be acceptable but would be at significant risk of being rejected
4. **accepted & awaiting PR** - it's been determined the suggested changes are OK and a
   PR would be welcomed (`S: accepted`)
5. **closed**: - the issue has been resolved, reasons include:
   - the suggested changes were implemented
   - it was rejected (due to technical concerns, ethos conflicts, etc.)
   - duplicate of a pre-existing issue or is invalid

**Note**: documentation issues don't use the `S: accepted` label currently since they're
less likely to be rejected.

## Labelling

We use labels to organize, track progress, and help effectively divvy up work.

Our labels are divided up into several groups identified by their prefix:

- **T - Type**: the general flavor of issue / PR
- **C - Category**: areas of concerns, ranges from bug types to project maintenance
- **F - Formatting Area**: like C but for formatting specifically
- **S - Status**: what stage of resolution is this issue currently in?
- **R - Resolution**: how / why was the issue / PR resolved?

We also have a few standalone labels:

- **`good first issue`**: issues that are beginner-friendly (and will show up in GitHub
  banners for first-time visitors to the repository)
- **`help wanted`**: complex issues that need and are looking for a fair bit of work as
  to progress (will also show up in various GitHub pages)
- **`ci: skip news`**: for PRs that are trivial and don't need a CHANGELOG entry (and
  skips the CHANGELOG entry check)
- **`ci: build all wheels`**: when a full wheel build is needed, such as to debug
  platform-specific issues. Black does not build wheels for every platform on each pull
  request because the full build matrix is expensive. After the label is added, the
  workflow starts only when a new commit is pushed.

```{note}
We do use labels for PRs, in particular the `ci: skip news` label, but we aren't that
rigorous about it. Just follow your judgement on what labels make sense for the specific
PR (if any even make sense).
```

## Projects

For more general and broad goals we use projects to track work. Some may be longterm
projects with no true end (e.g. the "Amazing documentation" project) while others may be
more focused and have a definite end (like the "Getting to beta" project).

```{note}
To modify GitHub Projects you need the
[Write repository permission level or higher](https://docs.github.com/en/organizations/managing-access-to-your-organizations-repositories/repository-permission-levels-for-an-organization#repository-access-for-each-permission-level).
```

## Closing issues

Closing an issue signifies the issue has reached the end of its life, so closing issues
should be taken with care. The following is the general recommendation for each type of
issue. Note that these are only guidelines and if your judgement says something else
it's totally cool to go with it instead.

For most issues, closing the issue manually or automatically after a resolving PR is
ideal. For bug reports specifically, if the bug has already been fixed, try to check in
with the issue opener that their specific case has been resolved before closing. Note
that we close issues as soon as they're fixed in the `main` branch. This doesn't
necessarily mean they've been released yet.

Design and enhancement issues should be also closed when it's clear the proposed change
won't be implemented, whether that has been determined after a lot of discussion or just
simply goes against _Black_'s ethos. If such an issue turns heated, closing and locking
is acceptable if it's severe enough (although checking in with the core team is probably
a good idea).

User support issues are best closed by the author or when it's clear the issue has been
resolved in some sort of manner.

Duplicates and invalid issues should always be closed since they serve no purpose and
add noise to an already busy issue tracker. Although be careful to make sure it's truly
a duplicate and not just very similar before labelling and closing an issue as
duplicate.

## Common reports

Some issues are frequently opened, like issues about _Black_ formatted code causing E203
messages. Even though these issues are probably heavily duplicated, they still require
triage sucking up valuable time from other things (although they usually skip most of
their lifecycle since they're closed on triage).

Here's some of the most common issues and also pre-made responses you can use:

### "The trailing comma isn't being removed by Black!"

```text
Black used to remove the trailing comma if the expression fits in a single line, but this was changed by #826 and #1288. Now a trailing comma tells Black to always explode the expression. This change was made mostly for the cases where you _know_ a collection or whatever will grow in the future. Having it always exploded as one element per line reduces diff noise when adding elements. Before the "magic trailing comma" feature, you couldn't anticipate a collection's growth reliably since collections that fitted in one line were ruthlessly collapsed regardless of your intentions. One of Black's goals is reducing diff noise, so this was a good pragmatic change.

So no, this is not a bug, but an intended feature. Anyway, [here's the documentation](https://github.com/psf/black/blob/master/docs/the_black_code_style.md#the-magic-trailing-comma) on the "magic trailing comma", including the ability to skip this functionality with the `--skip-magic-trailing-comma` option. Hopefully that helps solve the possible confusion.
```

### "Black formatted code is violating Flake8's E203!"

```text
Hi,

This is expected behaviour, please see the documentation regarding this case (emphasis mine):

> PEP 8 recommends to treat : in slices as a binary operator with the lowest priority, and to leave an equal amount of space on either side, **except if a parameter is omitted (e.g. ham[1 + 1 :])**. It recommends no spaces around : operators for “simple expressions” (ham[lower:upper]), and **extra space for “complex expressions” (ham[lower : upper + offset])**. **Black treats anything more than variable names as “complex” (ham[lower : upper + 1]).** It also states that for extended slices, both : operators have to have the same amount of spacing, except if a parameter is omitted (ham[1 + 1 ::]). Black enforces these rules consistently.

> This behaviour may raise E203 whitespace before ':' warnings in style guide enforcement tools like Flake8. **Since E203 is not PEP 8 compliant, you should tell Flake8 to ignore these warnings**.

https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#slices

Have a good day!
```
