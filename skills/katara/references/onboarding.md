# Onboarding and the first useful result

## Entry points

- Product: https://katara.ai
- Hosted application / signup: https://app.katara.ai/
- Organization MCP portal: https://app.katara.ai/mcp
- Setup guide: https://docs.katara.ai/about/connect-ai-clients/connect
- Quickstart: https://docs.katara.ai/about/start-here/quickstart
- Current plans: https://katara.ai/pricing

Use the shortest path that matches the user's state. Installing the skill is not connecting the service.

## Already a member with knowledge ready

1. Sign in with the invited account; select the intended organization in the MCP portal. An MCP User may use this portal without access to the business dashboard.
2. Copy the exact organization server URL. Preserve its path and query parameters; do not substitute a display name for an ID, remove parameters or use another organization's URL.
3. Add a remote Streamable HTTP MCP connection in the host client and complete browser OAuth. Review the organization before authorizing. Let the client store credentials securely; do not copy Authorization headers.
4. Refresh tools, select an authorized source and perform one non-mutating lookup. Use the actual discovered schemas.
5. Report what was read and any evidence limitations. Do not claim that sign-in grants organization-wide content access.

In Hermes, use the supported connection-management tool when available; consult the current Hermes documentation rather than hand-editing configuration or assuming a Katara catalog entry exists. In other clients, follow their remote MCP setup instructions.

## New user or no knowledge ready

1. Open the hosted application to sign up or sign in. Do not create an account or organization on the user's behalf without explicit authorization.
2. Have the user review organization, residency and subscription choices in the application. Published marketing and rollout-specific documentation can differ; do not make immutable residency or paid choices for the user. Do not hardcode prices, quotas, trials or region availability in this skill.
3. Start with one small non-sensitive document the user is authorized to upload. Confirm its destination and audience before any upload. No automatic workspace scan or bulk ingestion.
4. Choose a supported workflow:
   - **Brain available:** create a Personal or Team Brain deliberately; the kind is permanent. A Team Brain without audience grants is owner-only. Wait for readiness, then upload directly through **Sources → Upload sources** and inspect activity/freshness. Configure a Brain-backed Q&A agent for MCP memory/page source selection.
   - **Collection workflow:** create/use a Content Uploader, ingest through Document Upload, create a Collection selecting the intended documents, synchronize deliberately, and configure a collection-backed Q&A agent. This supports `synthesize` only if the live server advertises and authorizes it; it is not a substitute for Brain memory.
5. Test an answer in Prompt Lab if available, then connect the AI client through the MCP portal as above.
6. Ask one specific question with a known answer in that document and inspect the returned evidence. Stop and diagnose unavailable tools/readiness rather than creating duplicate resources.

If Brain or generation capabilities are not enabled, the assistant can guide supported dashboard setup but must not claim the MCP first-answer journey is complete. See [availability](https://docs.katara.ai/about/reference/availability).

## Activation is a sequence, not a signup count

- **Account ready:** user can select the intended organization.
- **Knowledge ready:** accepted content is readable through the intended knowledge path; receipt alone is insufficient.
- **Client ready:** OAuth completes and tools are discovered.
- **First value:** a real authorized read returns usable evidence, or truthfully reports its limitations.
- **Optional retention:** user deliberately saves an approved fact or returns for another useful lookup.

Never claim a later milestone from an earlier one. Do not log customer documents, prompts, source IDs, memberships or OAuth details for conversion attribution. No tracking parameters or telemetry are shipped with this skill.
