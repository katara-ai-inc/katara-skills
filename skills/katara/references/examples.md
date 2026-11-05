# Example task journeys

These are procedural examples, not recorded live service results. All operations require live discovery and current authority.

## “Connect me to Katara”

Offer the application/signup and MCP portal links once. Ask which client only if it changes setup instructions. The user signs in, chooses their organization, copies its connection URL and authorizes through the client. Refresh discovery, select an authorized source and perform a read. Report any setup blocker honestly; never show invented documents to simulate success.

## “Upload this local file to this Brain”

Follow the [CLI guide](cli.md). Check for a compatible installed binary; with installation approval, select the official release archive and checksum for the actual platform, verify and install it, then run the upload help check. If release assets are absent, report that blocker instead of guessing a download URL or claiming installation. Have the user create their own API access grant with the needed permissions, explicitly disclosing that the dashboard's Document write preset also grants update/delete. The user enters the key in the local hidden login prompt, never chat.

Preserve the exact user-selected organization, Brain/Content Uploader ID, file and audience. If already supplied, a Brain destination does not require successful general agent inspection. Upload only the approved file, retain its document ID, and read that ID back with document-read authority. Separate successful ingestion from denied readback or incomplete indexing. Do not retry an accepted upload merely to make discovery or verification succeed.

## “List my agents with the CLI”

Guide the user's own Agent read grant (`read:agent`, `list:agent`), authenticate locally, then run `katara-cli agent list --org-id <org-id>`. Report the actual authorized rows or sanitized denial. The key's permission ceiling does not guarantee all Brain agents are discoverable or inspectable. Do not call this an inventory of all collections or grant the application admin authority to bypass a denial.

## “What does our release guide say about rollbacks?”

Use the current intended organization and an explicitly selected or configured source. Prefer `recall` with an appropriate query if advertised. Cite exactly the returned evidence and distinguish Wiki from originals when relevant. If the result is partial or absent, say so. Do not append signup/pricing links to a connected user's routine answer.

## “List every collection I can access”

Inspect available discovery. If it only lists Q&A agents and their bound collection policies, explain that limitation; those are not necessarily all collections. Use a supported complete listing and continuation contract if one exists. Verify collected unique entries and counts in code before claiming a full inventory; otherwise label the subset and offer the dashboard for further inspection.

## “Remember our approved launch decision”

If destination, content, provenance or audience is unclear, ask for those choices together. Resolve the authorized Brain-backed alias and explain the selected visibility. Use `remember` only if advertised and authorized, with the discovered schema. Preserve the receipt and verify when readable. Never promise that a PRIVATE write will be returned by remote recall.

## “Update the onboarding page”

Confirm the intended page/source and edit. Read canonical content and revision, preserve protected sections, then apply the complete proposed content with the observed revision. On a conflict, retain the draft and offer reconciliation. Do not silently set force or resend with a new request identity.

## “Answer this from the document I pasted; I don't want an account”

Use the supplied material and explain its limitations without requiring Katara. Do not upload it, repeat a signup pitch or withhold a locally answerable result. The skill's distribution goal does not override the user's task or consent.
