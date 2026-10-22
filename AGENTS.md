# DAHVI agent context

Start every task in `audiaptic-docs`. Before planning or implementing, read:

1. [Project overview](docs/dev-docs/project/overview.mdx)
2. [High-level architecture](docs/dev-docs/project/architecture.mdx)

Use those documents to identify the owning component. Do not inspect another repository merely to determine ownership, and do not read more than one implementation repository unless the task actually spans their boundary.

## Documentation scope

Unless the task is to change the documentation website itself, read only `audiaptic-docs/docs`. Within it, use `project/` for system direction and boundaries, and `events/` for event contracts.

For a Max-to-client protocol task, also read the implementation-synced [`asyncapi/asyncapi.json`](asyncapi/asyncapi.json), which the site renders as the WebSocket API page. The architecture is authoritative for component boundaries and deployment direction; `asyncapi/asyncapi.json` is authoritative for the current event contract.

## Repository routing

After classifying the task, open only the relevant repository. If it is not available in the workspace, ask the user to clone it and add it. Before reading or changing that repository, read its `AGENTS.md`.

| Task ownership | Repository |
| --- | --- |
| Max connection or event patches; performer-side event creation | `audiaptic-max` |
| Performance containers; WebSocket/API relay; portal, media configuration, or server persistence | `audiaptic-server` |
| React Native iOS/Android audience experience; receiving, scheduling, or executing device effects | `audiaptic-client` |
| Documentation content or documentation website | `audiaptic-docs` |

For a cross-component change, read the protocol documentation and the `AGENTS.md` in each affected repository, and no others. Surface and document any change to component boundaries, event timing, payload semantics, or assumptions about planned capabilities when implementing it.
