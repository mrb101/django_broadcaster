Contributing
===========

Thank you for considering contributing to Django Dispatch! This document outlines the process for contributing to the project.

Setting Up Development Environment
--------------------------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

       git clone https://github.com/mrb101/django-broadcaster.git
       cd django-broadcaster

3. Create a virtual environment and install development dependencies:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       pip install -e ".[dev]"

4. Set up pre-commit hooks:

   .. code-block:: bash

       pre-commit install

Development Workflow
------------------

1. Create a branch for your changes:

   .. code-block:: bash

       git checkout -b feature/your-feature-name

2. Make your changes and write tests for them
3. Run the tests to ensure they pass:

   .. code-block:: bash

       pytest

4. Run the linters to ensure code quality:

   .. code-block:: bash

       flake8
       black .
       isort .

5. Commit your changes with a descriptive commit message:

   .. code-block:: bash

       git commit -m "Add feature X"

6. Push your changes to your fork:

   .. code-block:: bash

       git push origin feature/your-feature-name

7. Create a pull request on GitHub

Pull Request Guidelines
---------------------

* Include tests for any new features or bug fixes
* Update documentation for any changed functionality
* Follow the code style of the project
* Write a clear and descriptive pull request description
* Link to any related issues

Running Tests
-----------

To run the test suite:

.. code-block:: bash

    pytest

To run tests with coverage:

.. code-block:: bash

    pytest --cov=django_broadcaster

Building Documentation
--------------------

To build the documentation locally:

.. code-block:: bash

    cd docs
    make html

The built documentation will be in the ``_build/html`` directory.

Release Process
-------------

1. Update version in ``__init__.py``
2. Update CHANGELOG.rst
3. Create a new release on GitHub
4. Build and upload to PyPI:

   .. code-block:: bash

       python -m build
       twine upload dist/*

Code of Conduct
-------------

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

We expect all contributors to:

* Be respectful and inclusive
* Be collaborative
* Gracefully accept constructive criticism
* Focus on what is best for the community
* Show empathy towards other community members
