## Overview

Docker image packaging for Jackrabbit.

## Versions

- Stable: `gluufederation/jackrabbit:4.2.0_01`
- Unstable: `gluufederation/jackrabbit:4.2.1_dev`

Refer to [Changelog](./CHANGES.md) for details on new features, bug fixes, or older releases.

## Environment Variables

The following environment variables are supported by the container:

- `GLUU_MAX_RAM_PERCENTAGE`: Value passed to Java option `-XX:MaxRAMPercentage`.
- `GLUU_JAVA_OPTIONS`: Java options passed to entrypoint, i.e. `-Xmx1024m` (default to empty-string).
