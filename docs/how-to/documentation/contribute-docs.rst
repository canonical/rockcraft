.. _how-to-contribute-to-rockcraft-documentation:

Contribute to Rockcraft documentation
=====================================

Tools and markup
----------------

Rockcraft's documentation is generated with Sphinx_, using reStructuredText_
as the markup language for the source files.

Documentation structure
-----------------------

The Rockcraft documentation is organised according to the `Diátaxis framework`_.
Additionally, some rules are used to ensure that code referred to by the
documentation is kept up-to-date and tested thoroughly.

Including code and commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All code-like content going into the documentation must be tested, especially
if it is supposed to be reproducible. Pages that include code snippets or
terminal commands need to provide this information in separate files that can
be included in the project's test infrastructure.

Categories of the documentation that use code snippets will each have their own
directory with a ``code`` folder within. For example, :file:`tutorial/code`
will hold code for the tutorial.

Each page that provides technical information to the reader in the form of code
snippets or commands, such as a tutorial or how-to guide, should have its own
folder within the :file:`code` directory and contain a :file:`task.yaml` file
for spread tests.
For example, the :file:`tutorial/hello-world.rst` tutorial refers to code
supplied in the :file:`tutorial/code/hello-world/task.yaml` file. Additional
YAML_ files can also be included when needed, as shown here:

.. code:: text

   tutorial
   ├─ hello-world.rst
   └─ code
      └─ hello-world
         ├─ task.yaml
         └─ rockcraft.yaml

These YAML files can also include more than just the snippets that appear in a
page. For example, they can include additional commands to set up a test
environment or clean up after the test has been run. Each snippet should be
delimited with comments that enable them to be conveniently extracted, as in
this example:

.. literalinclude:: ../code/get-started/task.yaml
   :start-at: [docs:snap-version]
   :end-at: [docs:snap-version-end]

When including code snippets in a page, use the reStructuredText
literalinclude_ directive with the ``start-after`` and ``end-before`` options
to extract the relevant lines of text. If the indentation of the quoted
code is excessive, use the ``dedent`` option to reduce it to an acceptable
level, as in this example:

.. literalinclude:: ../get-started.rst
   :language: rst
   :start-at: literalinclude:: code/get-started/task.yaml
   :end-at: :dedent: 2

Handling code snippets in this systematic way encourages reuse of existing code
snippets and helps to ensure that the documentation stays up-to-date.

Build the documentation
-----------------------

The :ref:`how-to-build-the-documentation` guide contains step-by-step instructions for
setting up a virtual environment and building the documentation.

.. _`Diátaxis framework`: https://diataxis.fr
.. _Sphinx: https://www.sphinx-doc.org
..
   #wokeignore:rule=master
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
..
   #wokeignore:rule=master
.. _literalinclude: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude
.. _YAML: https://yaml.org/
.. _`submit an issue`: https://github.com/canonical/rockcraft/issues/new/choose
.. _`create a fork`: https://github.com/canonical/rockcraft/fork
.. _`CONTRIBUTING`: https://github.com/canonical/rockcraft/blob/main/CONTRIBUTING.md


Making a contribution
---------------------

Report issues
~~~~~~~~~~~~~

If you have a request or found a problem with the documentation, then please
`submit an issue`_. These issues are supervised and regularly triaged by the
repository owners. If you don't receive an answer within 2 weeks, please reply
to your own issue asking for an update.

Propose changes
~~~~~~~~~~~~~~~

Community contributions are more than welcome. To become an external
contributor you should:

1. `create a fork`_ of the Rockcraft repository,
2. commit the changes to your fork (ideally to a new branch),
3. make sure to follow the project's `CONTRIBUTING`_ guidelines,
4. create a Pull Request against the ``main`` branch.

Similarly to new issues, new Pull Requests (PR) are also supervised
and regularly triaged by the repository owners. If the tests are passing
and you don't receive an answer within 2 weeks, please add a comment to your
own PR asking for an update.
