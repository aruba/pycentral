Installation Instructions
=========================

Python comes with a package management system, `pip <https://packaging.python.org/tutorials/installing-packages/#id17>`_. \
Pip can install, update, or remove packages from the Python environment. It can also do this for virtual environments. \
It is a good idea to create a separate virtual environment for this project. A guide to virtual environments can be found \
`here <https://docs.python-guide.org/dev/virtualenvs/>`_.

To use pip to install the pyaoscx package from the official Python Package Index, PyPI, excecute the following command:

.. code-block:: console

   pip3 install pycentral

To install package with extras `colorLog` which displays logs in color on stdout.

.. code-block:: console

   pip3 install pycentral[colorLog]

.. Important:: This package is compatible with Python 3. Python 2 is not supported.