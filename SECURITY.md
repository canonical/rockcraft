# Security policy

## Release cycle

Canonical tracks and responds to vulnerabilities in the latest patch of every
[current major release] of Rockcraft. For a list of supported bases, see the
[base] documentation.

Bases are tied to Ubuntu LTS releases. For example, the `ubuntu@24.04` base uses Ubuntu
24.04 LTS as its build and runtime environment. This means that Rockcraft's support
of bases aligns with the [Ubuntu LTS release cycle].

The most recent major release of Rockcraft will always support bases still in their
regular maintenance lifecycle. When a major release of Rockcraft drops support for a
base, the previous major release remains supported until the dropped base reaches the
end of its extended support lifecycle.

## Reporting a vulnerability

To report a security issue, file a [Private Security Report] with a description of the
issue, the steps you took to create the issue, affected versions, and, if known,
mitigations for the issue.

The [Ubuntu Security disclosure and embargo policy] contains more information about
what you can expect when you contact us and what we expect from you.

[current major release]: https://documentation.ubuntu.com/rockcraft/en/stable/release-notes/#current-releases
[base]: https://documentation.ubuntu.com/rockcraft/en/stable/reference/rockcraft.yaml/#base
[Private Security Report]: https://github.com/canonical/rockcraft/security/advisories/new
[Ubuntu Security disclosure and embargo policy]: https://ubuntu.com/security/disclosure-policy
[Ubuntu LTS release cycle]: https://ubuntu.com/about/release-cycle
