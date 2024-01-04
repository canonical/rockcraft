.. _publishslice:

How to publish a slice definition
*********************************

At this stage, you have created some package slice definitions and you have a
custom Chisel release in your local development environment. You have also
tested this custom Chisel release, and it works! You believe there are others
who could really use it as well, so **how can you make it accessible to
everyone**?

It is as simple as proposing your changes into the upstream
`Chisel releases repository <https://github.com/canonical/chisel-releases>`_:

1. Fork this repository https://github.com/canonical/chisel-releases and clone
   your fork:

.. code-block:: bash

    # Let's assume we are working with Ubuntu 22.04
    git clone -b ubuntu-22.04 https://github.com/<your_github_username>/chisel-releases.git

2. Create a branch:

.. literalinclude:: code/publish-slice/task.yaml
   :language: bash
   :start-after: [docs:new-branch]
   :end-before: [docs:new-branch-end]
   :dedent: 2

3. Add and commit your modifications:

.. code-block:: bash

   cp <path/to/your/slice/definitions/file> slices
   git add slices/
   git commit -m "feat: add new slice definitions for 'name_of_the_package'"
   git push origin create-openssl-bins-slice

Create a pull request and wait for it to be merged.

And that's it! Your custom Chisel release and new slice definitions are now
available in Chisel, and anyone can use them. **Congrats**! And thank you for
your contribution.
