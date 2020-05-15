## Overview

Docker image packaging for Jackrabbit.

## Versions

- Stable: `gluufederation/jackrabbit:4.1.1_01`
- Unstable: `gluufederation/jackrabbit:4.1.1_dev`

Refer to [Changelog](./CHANGES.md) for details on new features, bug fixes, or older releases.

## Environment Variables

The following environment variables are supported by the container:

- `GLUU_MAX_RAM_PERCENTAGE`: Used in conjunction with Docker memory limitations (`docker run -m <mem>`) to identify the percentage of the maximum amount of heap memory.
