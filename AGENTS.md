# DAHVI agent context

DAHVI (Distributed Audio Haptic Visual Interface) is a real-time, inclusive performance system. A Max-based performer sends timestamped events to a per-performance service, which distributes them to a connected audience using native React Native apps on iOS and Android. Audience devices execute events locally at their scheduled Unix-epoch time to coordinate audio, visual, haptic, caption, and flashlight effects.

Before planning or implementing work in this repository, read these canonical documents:

1. [Project overview](docs/dev-docs/project/overview.mdx)
2. [High-level architecture](docs/dev-docs/project/architecture.mdx)

For work involving the Max-to-client protocol, read the implementation-synced [WebSocket API](docs/dev-docs/events/websocket-api.mdx). Its source specification is [`asyncapi/asyncapi.json`](asyncapi/asyncapi.json), which the server workflow updates from implemented schemas.

## Decision hierarchy

- The high-level architecture is authoritative for current component boundaries and deployment direction.
- The implementation-synced AsyncAPI specification is authoritative for the current event contract. The pages in `docs/dev-docs/events-legacy/` are historical reference only and can diverge from implementation.
- The original project proposal is historical context. Its browser-only client has been intentionally superseded by the native mobile-app decision because iOS browsers could not provide the required haptic and lighting behavior.

## Important current constraints

- The live event flow is currently one way: Max -> performance container -> mobile devices.
- A performance is isolated in a Docker container on the DAVHI server; its state is temporary unless stored separately.
- Media is configured per performance and stored in Cloudflare R2, outside the real-time relay path.
- Zones, audience-to-Max input, multi-performance administration, and a more complete portal UI are planned work, not baseline behavior.

If a proposed change crosses a component boundary, changes event timing or payload semantics, or assumes a planned capability already exists, surface the decision and update the relevant canonical documentation with the implementation.
