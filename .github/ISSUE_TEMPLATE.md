Howdy! Sorry you're having trouble. To expedite your experience,
provide some basics for me:

Operating system:
Python version:
*Black* version:
Does also happen on master:

To answer the last question, you have two options:
1. Use the online formatter at https://black.now.sh/?version=master, which will use the latest master branch.
2. Or run black on your machine:
    * create a new virtualenv (make sure it's the same Python version);
    * clone this repository;
    * run `pip install -e .`;
    * make sure it's sane by running `python setup.py test`; and
    * run `black` like you did last time.
