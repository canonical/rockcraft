
**********************************
Rockcraft documentation guidelines
**********************************

The Rockcraft documentation pages adopt the `Diátaxis framework <https://diataxis.fr/>`_.

Contributing to the docs
------------------------

Rockcraft's documentation is generated with Sphinx, and we use reStructuredText as the
markup language for the source files.

Code blocks
***********

All code-like content going into the documentation must be tested, especially if said content
is supposed to be reproducible.

Whenever applicable, sections with code snippets will have their own directory, with a
``code`` folder within (e.g. ``tutorials/code``). 

Each technical page (i.e. a tutorial, a how-to guide, etc.) shall have its own folder within
the ``code`` directory (e.g. ``tutorials/code/hello-world``).

Finally, each page shall have a corresponding ``task.yaml`` file for Spread tests, and use ``..  literalinclude::`` 
to include code blocks from those YAML files. 

Build the docs
--------------

.. include:: how-to/build-docs.rst
