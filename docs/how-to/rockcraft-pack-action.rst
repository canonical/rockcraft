How to build a ROCK with Rockcraft's GitHub Action
**************************************************

Within your GitHub repository, make sure you have
`GitHub Actions enabled <https://docs.github.com/en/actions/quickstart>`_.

Navigate to ``.github/workflows``, open the YAML file where you want the ROCK
build to take place, and add the following steps:

.. literalinclude:: code/rockcraft-pack-action/rockcraft-pack.yaml
    :language: yaml

Commit the changes and push. GitHub shall then trigger a new workflow
execution and with it, Rockcraft will be set up and used to pack your ROCK,
based on whatever ``rockcraft.yaml`` file there is at your project's root.

To know how to publish this ROCK outside the GitHub build environment, and how
to pass additional inputs parameters to this action, please refer to the
`action's
documentation <https://github.com/canonical/craft-actions#rockcraft-pack>`_.



