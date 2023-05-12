How to create a package slice for Chisel
****************************************

If your package doesn't yet have the slice definitions you actually need to
**create your own slice definition** (which you can, later on, propose to be
merged upstream for everyone else to use :ref:`publishslice` ).

**Let's assume you are trying to create a slice definition for installing the
OpenSSL binary into your ROCK!**

Make sure the slice definition doesn't exist yet
------------------------------------------------

To avoid re-creating a slice, check the following to see if something that fits
your needs already exists:

#. Look into the upstream `chisel-releases`_ repository
#. Switch to the branch corresponding to the desired Ubuntu release for your
   ROCK
#. Search your package name within the list of slice definitions files

   * if you find it, open it and try to find a slice name containing the bits
     and pieces you need from that package


Structure of a slice definitions file
-------------------------------------

There can be only **one slice definitions file** for each Ubuntu package. All of
the slice definitions files follow the same structure:

.. code-block:: yaml

    # (req) Name of the package.
    # The slice definition file should be named accordingly (eg. "openssl.yaml")

    package: <package-name>

    # (req) List of slices
    slices:

        # (req) Name of the slice
        <slice-name>:

            # (opt) Optional list of slices that this slice depends on
            essential:
              - <pkgA_slice-name>
              - ...

            # (req) The list of files, from the package, that this slice will install
            contents:
                </path/to/content>:
                </path/to/another/multiple*/content/**>:
                </path/to/moved/content>: {copy: /bin/original}
                </path/to/link>: {symlink: /bin/mybin}
                </path/to/new/dir>: {make: true}
                </path/to/file/with/text>: {text: "Some text"}
                </path/to/mutable/file/with/default/text>: {text: FIXME, mutable: true}
                </path/to/temporary/content>: {until: mutate}

            # (opt) Mutation scripts, to allow for the reproduction of maintainer scripts,
            # based on Starlark (https://github.com/canonical/starlark)
            mutate: |
                ...

Find the dependencies of your package
-------------------------------------

Find the dependencies of the package for which you want to create a new slice
definition (``openssl`` in this guide) with this command:

.. literalinclude:: code/create-slice/task.yaml
    :language: bash
    :start-after: [docs:apt-show-openssl]
    :end-before: [docs:apt-show-openssl-end]
    :dedent: 2

The output will be similar to:

..  code-block:: text
    :emphasize-lines: 1,2,7
    :class: log-snippets

    package: openssl
    Version: 3.0.2-0ubuntu1.7
    Origin: Ubuntu
    Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
    Original-Maintainer: Debian OpenSSL Team <pkg-openssl-devel@alioth-lists.debian.net>
    Bugs: https://bugs.launchpad.net/ubuntu/+filebug
    Depends: libc6 (>= 2.34), libssl3 (>= 3.0.2-0ubuntu1.2)

From the above output, you can confirm that ``openssl`` **depends on** ``libc6``
and ``libssl3``. So when creating your slice definitions file for OpenSSL, you
will need to remember to include those packages' slices as a dependency as well,
whenever needed. Let's do that in the following section.

Create your slice definition
----------------------------

You now have everything needed to actually define the OpenSSL slice that will
install the content you are looking to have in the final ROCK. Since you are
looking to install just the OpenSSL binaries from the ``openssl`` package, what
about naming this new slice **bins**? Let's go for it:

#. **What is the name of your slice definitions file?**
   It is a YAML file called ``openssl.yaml``
#. **What package name should be defined inside this file?**
   The package name is ``openssl``
#. **What is your slice name?**
   It should be called ``bins``
#. **What contents do you need from the OpenSSL package?**
   Just the binaries - ``/usr/bin/c_rehash`` and ``/usr/bin/openssl``
#. **Does your slice depend on any other package slice?** Yes, OpenSSL depends
   on ``libc6`` and ``libssl3``

   * **Do these two packages have slice definitions files upstream?** Yes, there
     is already a slice definitions file for `libc6`_ and another one for
     `libssl3`_. If these dependencies were not present in the upstream Chisel
     release, you would also need to create their corresponding slice
     definitions
   * **Which slices do you depend on then?** Since you only want the OpenSSL
     binaries, you might only need the libraries from ``libc6`` and ``libssl3``,
     as well as the configuration files from ``libc6`` and ``openssl``
     themselves.


Create a new YAML file named ``openssl.yaml``, with the following content:

.. literalinclude:: code/create-slice/openssl.yaml
    :language: yaml

Notice the unforeseen new slice ``config``. Because your OpenSSL binaries depend
on the OpenSSL configuration files, and those were not yet present anywhere in
the Chisel releases upstream, you also need to create that slice! You may also
ask **"why not put those configuration files inside the "bins" slice"**? You
could! But we recommend, as a best practice, to separate and group contents
according to their nature, as you may tomorrow need to create a new slice
definition that only needs the OpenSSL configurations and not the binaries.

And that's it. This is your brand new slice definitions file, which will allow
Chisel to install **just** the OpenSSL binaries (and their dependencies) into
your ROCK! To learn about how to actually use this new slice definition file and
publish it upstream for others to use, please check the following guides.

.. _chisel-releases:
  https://github.com/canonical/chisel-releases/tree/ubuntu-22.04/slices
.. _libc6:
  https://github.com/canonical/chisel-releases/blob/ubuntu-22.04/slices/libc6.yaml
.. _libssl3:
  https://github.com/canonical/chisel-releases/blob/ubuntu-22.04/slices/libssl3.yaml
