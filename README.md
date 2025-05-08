# Rockcraft

[![Snap Status](https://snapcraft.io/rockcraft/badge.svg)](https://snapcraft.io/rockcraft)
[![Documentation Status](https://readthedocs.com/projects/canonical-rockcraft/badge/?version=stable)](https://documentation.ubuntu.com/rockcraft/en/stable/?badge=stable)

## Purpose

Tool to create OCI Images using the language from
[Snapcraft](https://snapcraft.io) and [Charmcraft](https://juju.is).

## Installing

Install Rockcraft from the Snap Store

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/rockcraft)

## Documentation

Documentation on the usage of the tool and tutorial can be found on
<https://documentation.ubuntu.com/rockcraft/en/stable/>

## Testing

In addition to unit tests in `tests/unit`, which can be run with
`make test-units`, a number of integrated tests in `tests/spread` can be
run with [Spread](https://github.com/snapcore/spread). See the [general
notes](https://github.com/snapcore/snapcraft/blob/main/TESTING.md#spread-tests-for-the-snapcraft-snap)
and take note of these `rockcraft`-specific instructions:

-   Initialize/update git submodules to fetch Spread-related helper
    scripts:

    ``` 
    $ git submodule init
    $ git submodule update
    ```

-   Spread needs a `rockcraft` snap in order to run. Create one with
    `snapcraft` via:

    ``` 
    $ snapcraft --use-lxd
    $ cp <generated snap> tests/
    ```

-   Run Spread:

    ``` 
    $ spread tests/spread
    # Or run a specific test
    $ spread tests/spread/tutorial/basic
    # Use "-v" for verbose, and "-debug" to get a shell if the test fails
    $ spread -v -debug tests/spread/tutorial/basic
    ```
