# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs
Report bugs at https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitLab issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

## Implement Features

Look through the GitLab issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

## Write Documentation

Archer Tools could always use more documentation, whether as
part of the official Archer Tools docs, in docstrings, or
even on the network in blog posts, articles, and such.

## Submit Feedback

The best way to send feedback is to file an issue at https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is not the only project we're responsible for, and that
  contributions are welcome :)

## Get Started

Ready to contribute? Here's how to set up `archer_tools` for local development.

1. Fork the `archer_tools` repo on GitLab.
2. Clone your fork locally::

    $ git clone git@sc.appdev.proj.coe.example.com:<your_name_here>/archer_tools.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv archer_tools
    $ cd archer_tools/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

    Now you can make your changes locally.

5. When you're done making changes, check that you changes pass flake8 and the
    tests, including testing other Python versions with tox::

    $ pip install tox
    $ tox -- archer_tools

6. Commit your changes using commitizen and push your branch to GitLab::

    $ git cz -a
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a merge request through the GitLab website.

## Merge Request Guidelines

Before you submit a merge request, check that it meets these guidelines:

1. The merge request should include tests.
2. If the merge request adds functionality, the docs should be updated. Put
    your new functionality into a function with a docstring, and add the
    feature to the list in README.md
3. The merge request should work for Python 3.6.
4. Use the GitLab merge request template to write the description

## Tips

To run a subset of tests::

$ py.test tests.test_archer_tools


## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.md) and
submitted in a merge request. After the merge request is merged, GitLab CI will
then deploy to PyPI if tests pass and the version is bumped successfully.
