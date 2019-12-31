.. highlight:: shell

============
Installation
============


Stable release
--------------

To install Archer Tools, run this command in your terminal:

.. code-block:: console

    $ pip install archer_tools

This is the preferred method to install Archer Tools, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Once you have python/pip installed, configure them with the following

Install a single Pypi Package

.. code-block:: console

    pip install <package-name> --index-url=https://pypi.tsecm.example.com/simple/ --trusted-host=pypi.tsecm.example.com

Update all pip commands to use custom Pypi repo

Create/modify file ~/.pip/pip.conf (on Windows, ~/.pip/pip.ini) with the following

.. code-block:: ini

    [global]
    index = https://pypi.tsecm.example.com/simple/
    index-url = https://pypi.tsecm.example.com/simple/
    trusted-host = pypi.tsecm.example.com

Update all easy_install commands to use custom Pypi repo

Create/modify file ~/.pydistutils.cfg with the following:

.. code-block:: ini

    [easy_install]
    index = https://pypi.tsecm.example.com/simple/
    index-url = https://pypi.tsecm.example.com/simple/
    trusted-host = pypi.tsecm.example.com

From sources
------------
You can install the project using pip over git

.. code-block:: console

    $ pip install git+ssh://git@sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools.git

Or the source for Archer Tools can be downloaded from the `GitLab repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git@sc.appdev.proj.coe.example.com:ceg/cmd/archer/archer_tools.git

Or download the `tarball`_:

.. code-block:: console

    $ curl -OL https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools/repository/archive.tar.gz?ref=master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

.. _Gitlab repo: https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools
.. _tarball: https://sc.appdev.proj.coe.example.com/ceg/cmd/archer/archer_tools/repository/archive.tar.gz?ref=master
