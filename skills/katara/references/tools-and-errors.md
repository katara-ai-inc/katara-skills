# Tools, source selection and recovery

The live server's discovered names and schemas are authoritative. This is a routing guide, not a promise of deployed availability or a replacement JSON schema.

## Operation routing

| Intent | Advertised operation to consider | Boundary |
| --- | --- | --- |
| Find facts / query evidence | `recall` | Query evidence is distinct from fact-only reads; preserve coverage and evidence filters. |
| Inspect a known entity | `entity` | Deterministic card, not a generated answer. |
| Generate a grounded answer | `synthesize` | Requires a question; potentially billable and rollout-dependent. |
| Read a Wiki page | `get_page` | Use returned content/revision, not a guessed URL. |
| Save an approved fact | `remember` | Nonblank provenance; deliberate audience and destination. |
| Retire a fact | `forget` | Fact retirement, not deletion of underlying history or source files. |
| Edit a Wiki page | `put_page` | Full canonical content; revision checks and protected content apply. |
| Assemble context / inspect updates | `context_pack`, `delta` | WORLD-only; not a complete change/deletion feed. |
| Discover policies | `list_agents`, `get_agent` | Authorized agent metadata, not exhaustive collection enumeration or secrets. |
| Ingest through an uploader | `upload_document` | Inspect its schema; its ingestion `source_id` is not a memory alias. |
| Synchronize one collection | `sync_collection` | Explicit `collection_id`; changes indexed data, not Brain refresh. |

For memory/page operations, a concrete `source_id` is an authorized Q&A policy alias. All require a Brain-backed alias except explicitly selected collection-backed `synthesize`. Selecting an alias neither grants permissions nor changes a saved default. Never guess an ID or fall back to a different source after denial.

Do not hand-build tool payloads from this table: inspect required fields, enum casing, bounds, revision/request UUID rules and result schemas from discovery before use.

## Recovery

| Observation | Safe response |
| --- | --- |
| No connection / authentication required | Use the client's browser OAuth connection flow and the portal's exact organization URL. Never request a token in chat. |
| No organization available | Check the invited account and ask an organization administrator about membership. Do not create duplicate organizations. |
| `DEFAULT_SOURCE_REQUIRED` | An explicit default is missing for this organization and verified user/client or credential. Select an authorized concrete alias for this call, or guide a deliberate default-setting step. This is not proof of denied resource access. |
| Default unavailable / `SOURCE_NOT_FOUND` | Verify the exact alias, lifecycle and current permissions. Do not choose a replacement silently. |
| `SCOPE_DENIED` / permission denied | Preserve the sanitized structured detail; check current organization, role, credential grants and target authority. Do not promise that re-login, buying a plan or OAuth scope changes will grant access. |
| Tool missing | Refresh discovery and check rollout with the administrator. Do not substitute retired answer/source/loader tools. |
| Read-only user attempts a write | Explain that MCP User is read-only and target contribution rights also matter; do not attempt to elevate the role. |
| Rate/usage limit | Honor the server's retry guidance, avoid loops and show current pricing only if relevant/requested. No automatic purchase or upgrade. |
| Write conflict / pending or uncertain result | Retain the draft, request UUID and arguments. Reconcile via supported status/readback or original idempotent retry, never silent force or a new intent. |
| Upload accepted, answer still stale | Distinguish ingestion, indexing, refresh and query readiness; inspect supported activity rather than repeat-uploading. |
| Empty or degraded evidence | Report selected source, scope and coverage; do not call it an exhaustive absence finding. |

Human OAuth identifies the user/client; current backend role/resource checks determine access. Katara-issued API/application credentials may have additional stored grants. Do not embed a fixed scope-upgrade recipe: deployed authorization can differ from older documentation. Never disable audience, membership or resource validation to repair a connection.

`world` visibility is bounded to authorized Brain readers. `private` writes cannot be recalled remotely, including by the author. `delta` may begin with an empty result for a new/idle session; missing updates do not prove a cached page is still authorized. Honor current authorization on every access.

Public references: [Connection setup](https://docs.katara.ai/about/connect-ai-clients/connect), [tools and sources](https://docs.katara.ai/about/connect-ai-clients/tools), [availability](https://docs.katara.ai/about/reference/availability). These guides describe contracts and rollout-dependent workflows; they are not live certification.
