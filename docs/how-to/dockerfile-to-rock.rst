How to convert a Dockerfile to a ROCK
*************************************

Understand
----------
Read the dockerfile. Look at the different parts and bases.
You may want to `generate a diagram`_ of the Dockerfile.

.. _generate a diagram: https://github.com/patrickhoefler/dockerfilegraph

Spot all the different parts of the Dockerfile and create a
blank `part` subsection for each. For example:

  .. code-block::
    parts:
      backend:
        source: .
      frontend:
        after: [backend]
        source: .

Prototype with the nil plugin
-----------------------------
With the nil plugin you would need to be quite involved in
the build process, as this would be as close as it gets to
the original Dockerfile, in terms of shell commands.

  .. code-block::
    parts:
      backend:
        build-environment:
          - FOO: "bar"
        override-build: |
            echo "hello $FOO" > world
            cp world $CRAFT_STAGE
        override-stage: |
            cp world $CRAFT_PRIME

You can examine the result of individual parts by passing
the ``shell-after`` argument:

  .. code-block::
    rockcraft -v build backend --shell-after

If the step fails, you can use ``debug`` instead:

  .. code-block::
    rockcraft -v build backend --debug


Replace the nil plugin with dedicated plugins
---------------------------------------------
For example:

- Manually copying from ``$CRAFT_STAGE`` to ``$CRAFT_PRIME``
  and/or running ``craftctl default`` may not be necessary anymore
  if you use the ``dump`` plugin.
- ``pip install`` commands could be replaced by the
  ``python-requirements`` and ``python-packages`` statements
  of the python plugin.

