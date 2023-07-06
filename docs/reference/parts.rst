
.. _ref_parts:

***************
Rockcraft parts
***************

.. rubric:: The main building blocks of a ROCK are *parts*.

If this sentence sounds familiar, it's because **it is familiar**!
Rockcraft parts are inherited from other existing Craft tools like
`Snapcraft`_ and `Charmcraft`_.

Rockcraft *parts* go through the same lifecycle steps as Charmcraft and
`Snapcraft parts <https://snapcraft.io/docs/parts-lifecycle>`_.

The way the *parts*' keys and values are used in the *rockcraft.yaml* is exactly
the same as in `snapcraft.yaml`_
(`here <https://snapcraft.io/docs/adding-parts>`_ is how you define a *part*).

Albeit being fundamentally identical to Snapcraft parts, Rockcraft parts
actually offer some extended functionality and keywords:

* **stage-packages**: apart from offering the well-known package installation
  behaviour, in Rockcraft the ``stage-packages`` keyword actually supports
  chiselled packages as well (:ref:`learn more about Chisel
  <chisel_explanation>`).
  To install a package slice instead of the whole package, simply follow the
  Chisel convention *<packageName>_<sliceName>*.


Example
.......

.. _chisel-example:

.. code-block:: yaml

  parts:
    chisel-openssl:
      plugin: nil
      stage-packages:
        - openssl_bins
        - ca-certificates_data

    package-hello:
      plugin: nil
      stage-packages:
        - hello


NOTE: at the moment, it is not possible to mix packages and slices in the same
stage-packages field.

.. _snapcraft.yaml: https://snapcraft.io/docs/snapcraft-parts-metadata
