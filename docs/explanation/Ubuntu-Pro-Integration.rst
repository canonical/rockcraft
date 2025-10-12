.. _ubuntu_pro_integration_page:

Ubuntu Pro Integration
======================


Users subscribed to Ubuntu Pro can benefit from the enhanced security and
compliance features it offers in Rockcraft as well. Rocks built with the
`--pro` flag can be upgraded with Ubuntu Pro packages automatically.

There are some requirements to be met to use this features:
- The user must have an Ubuntu Pro subscription, and are only permitted to 
  build with Ubuntu Pro services they are entitled to.
- Ubuntu Pro must be enabled on the host system where the rock is built.
- The `build-base` and `base` fields in the `rockcraft.yaml` must be the same.
- The `build-base` field must be an Ubuntu LTS image.
- Images built with FIPS features can only be run on Ubuntu hosts of the same
  release and FIPS status.
- When building Ubuntu Pro enabled rocks with destructive mode, the host
  system must have the same version of Ubuntu as the rock's base, and have
  the same Ubuntu Pro services enabled as the rock.

To begin building images with Ubuntu Pro, the user must include the `--pro` flag
when building Rocks. This includes all lifecycle commands such as `pull`, 
`build` and `pack`. The `--pro` flag is passed, along with the Ubuntu Pro services
to be included in the rock. Multiple services can be specified by separating them
with commas. For example, to build a rock with the `esm-apps` and `esm-infra`
services, the command would be as follows:

```rockcraft pack --pro esm-apps,esm-infra```

When manually stepping through life-cycle steps of a rock, the `--pro` flag must be
included in all steps, and must remain the same throughout the lifecycle of the rock.
Changing the services or removing the `--pro` flag in any step will result in an error, and
can be corrected by performing a `rockcraft clean` and starting the lifecycle again.


Application Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When building rocks with Ubuntu Pro, the following changes are applied to the rock:
- Packages installed either as `build-packages` or `stage-packages` are installed
  from Ubuntu Pro repositories. This includes packages installed with chisel as 
  well. 
- Packages built from non-bare bases are upgraded with all Ubuntu Pro services passed
  to the `--pro` flag. In this process the Pro Services are transferred from the build
  environment to the rock's overlay. When building with destructive mode, any custom 
  sources such as PPAs will be preserved and may be installed in the rock during the
  build process.
- Currently upstream chisel-release sources do not support installing `openssl` slices
  in FIPS environments.
