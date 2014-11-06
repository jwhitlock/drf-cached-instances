============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/jwhitlock/drf-cached-instances/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

drf-cached-instances could always use more documentation, whether as
part of the official Cached Instances for Django REST Framework docs, in docstrings, or
even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at 
https://github.com/jwhitlock/drf-cached-instances/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up drf-cached-instances
for local development.

1. Fork the drf-cached-instances repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/drf-cached-instances.git

3. Install your local copy into a virtualenv. Assuming you have
   virtualenvwrapper installed, this is how you set up your fork for local
   development::

    $ mkvirtualenv drf-cached-instances
    $ cd drf-cached-instances/
    $ pip install -r requirements.txt
    $ ./manage.py syncdb

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ make qa-all

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.  Test coverage should be 100%, line
   and branch.
2. Follow PEP8 and PEP257.  ``make qa`` can be used to check compliance.
3. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
4. The pull request should work for Python 2.6, 2.7, 3.3, and 3.4. Check
   https://travis-ci.org/jwhitlock/drf-cached-instances/pull_requests and make
   sure that the tests pass for all supported Python versions.
   Use ``make qa-all`` to check locally.

Tips
----

To run a subset of tests::

    $ ./manage.py test tests/test_cache.py

To mark failed tests::

    $ ./manage.py test --failed

To re-run only the failed tests::

    $ ./manage.py test --failed
