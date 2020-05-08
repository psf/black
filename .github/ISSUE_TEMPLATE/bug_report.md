---
name: Bug report
about: Create a report to help us improve
title: ""
labels: bug
assignees: ""
---

**Describe the bug** A clear and concise description of what the bug is.

**To Reproduce** Steps to reproduce the behavior:

1. Take this file '...'
2. Run _Black_ on it with these arguments '....'
3. See error

**Expected behavior** A clear and concise description of what you expected to happen.

**Environment (please complete the following information):**

- Version: [e.g. master]
- OS and Python version: [e.g. Linux/Python 3.7.4rc1]

**Does this bug also happen on master?** To answer this, you have two options:

1. Use the online formatter at https://black.now.sh/?version=master, which will use the
   latest master branch.
2. Or run _Black_ on your machine:
   - create a new virtualenv (make sure it's the same Python version);
   - clone this repository;
   - run `pip install -e .`;
   - make sure it's sane by running `python -m unittest`; and
   - run `black` like you did last time.

**Additional context** Add any other context about the problem here.
