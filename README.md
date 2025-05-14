# Rockcraft

[![Rockcraft][rockcraft-badge]][rockcraft-site]
[![Documentation Status][rtd-badge]][rtd-stable]

**Rockcraft** is the command-line tool for building rocks, which are
OCI-compliant container images based on Ubuntu. It handles all the repetitive and boilerplate
steps of building a rock, directing your focus to what really matters – the rock's
content. From independent software vendors to container users of any experience level,
Rockcraft is for anyone who wants to build production-grade rocks.

## Basic usage

A rock's build configuration is stored in simple language as a project file called
`rockcraft.yaml`.

From the root of your container's codebase, Rockcraft creates a minimal `rockcraft.yaml` with:

```bash
rockcraft init
```

After you add all your container's packages and dependencies to the project file, bundle
the rock with:

```bash
rockcraft pack
```

## Installation

Rockcraft is available on all major Linux distributions.

Rockcraft has first-class support as a [snap](https://snapcraft.io/rockcraft). On
snap-ready systems, you can install it on the command line with:

```bash
snap install rockcraft --classic
```

## Documentation

The [Rockcraft documentation](https://documentation.ubuntu.com/rockcraft) provides
guidance and learning material about the full process of building a rock, debugging, the
command reference, and much more.

## Community and support

Ask your questions about Rockcraft and what's on the horizon, and see who's working on
what in the [Rockcraft Matrix channel](https://matrix.to/#/#rockcraft:ubuntu.com).

You can report any issues or bugs on the project's [GitHub
repository](https://github.com/canonical/Rockcraft/issues).

Rockcraft is covered by the [Ubuntu Code of
Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## Contribute to Rockcraft

Rockcraft is open source and part of the Canonical family. We would love your help.

If you're interested, start with the [contribution guide](HACKING.md).

We welcome any suggestions and help with the docs. The [Canonical Open Documentation
Academy](https://github.com/canonical/open-documentation-academy) is the hub for doc
development, including Rockcraft docs. No prior coding experience is required.

## License and copyright

Rockcraft is released under the [GPL-3.0 license](LICENSE).

© 2023-2025 Canonical Ltd.

[rockcraft-badge]: https://snapcraft.io/rockcraft/badge.svg
[rockcraft-site]: https://snapcraft.io/rockcraft
[rtd-badge]: https://readthedocs.com/projects/canonical-rockcraft/badge/?version=stable
[rtd-stable]: https://documentation.ubuntu.com/rockcraft/en/stable/?badge=stable
