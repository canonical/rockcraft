How to build the documentation
******************************

Create a virtual environment and activate it::

    python3 -m venv docs/env
    source docs/env/bin/activate

Install the documentation requirements::

    pip install -r requirements-doc.txt

Once the requirements are installed, you can use the provided ``Makefile`` to build the documentation::

    make docs  # the home page can be found at docs/_build/html/index.html

Even better, serve it locally on port 8080. The documentation will be rebuilt on each file change, and will reload the browser view.

    make rundocs
    