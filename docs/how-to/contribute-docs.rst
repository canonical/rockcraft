************************************************
How to contribute to the Rockcraft documentation
************************************************

Tools and markup
----------------

Rockcraft's documentation is generated with Sphinx_, using reStructuredText_
as the markup language for the source files.

Documentation structure
-----------------------

The Rockcraft documentation is organised according to the `Diátaxis framework`_.
Additionally, some rules are used to ensure that code referred to by the
documentation is kept up-to-date and tested thoroughly.

Code blocks
~~~~~~~~~~~

All code-like content going into the documentation must be tested, especially if
said content is supposed to be reproducible.

Whenever applicable, sections with code snippets will have their own directory,
with a ``code`` folder within; e.g. ``tutorials/code`` holds code for the
tutorials.

Each technical page, such as a tutorial or how-to guide, shall have its own
folder within the ``code`` directory; e.g. ``tutorials/code/hello-world`` for
a ``tutorials/hello-world.rst`` tutorial.

Finally, each page shall have a corresponding ``task.yaml`` file for Spread
tests, and use ``..  literalinclude::`` to include code blocks from those YAML
files.

Build the documentation
-----------------------

The :ref:`how_to_build_docs` guide contains step-by-step instructions for
setting up a virtual environment and building the documentation.

.. _`Diátaxis framework`: https://diataxis.fr
.. _Sphinx: https://www.sphinx-doc.org
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
