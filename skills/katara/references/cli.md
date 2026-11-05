# CLI installation, API keys and file uploads

Use the [official Katara CLI](https://github.com/katara-ai-inc/katara-cli) for local-file
uploads and shell/API agent listing. The CLI is a separate executable, not an MCP
server. MCP recall, Wiki and memory workflows keep using browser OAuth and do not
require this setup.

## 1. Agent: check and install the CLI

Inspect the actual host OS and process architecture. First check for `katara-cli`
and run `katara-cli document upload --help`. A compatible existing installation can
be reused; do not reinstall it for every task. Loading this skill does not authorize
installation. Follow host approval requirements, and obtain approval before
replacing an existing executable or modifying persistent shell configuration.

If installation is authorized, the agent should install a prebuilt binary from the
[official GitHub Releases](https://github.com/katara-ai-inc/katara-cli/releases), not
ask the user to install Rust. Inspect the chosen release's assets first and use its
exact tag for both the archive and checksum:

| Host | Archive | Extracted binary |
| --- | --- | --- |
| Linux x64 (glibc 2.35+) | `katara-cli-x86_64-unknown-linux-gnu.tar.gz` | `katara-cli` |
| Linux ARM64 (glibc 2.35+) | `katara-cli-aarch64-unknown-linux-gnu.tar.gz` | `katara-cli` |
| macOS Intel | `katara-cli-x86_64-apple-darwin.tar.gz` | `katara-cli` |
| macOS Apple Silicon | `katara-cli-aarch64-apple-darwin.tar.gz` | `katara-cli` |
| Windows x64 | `katara-cli-x86_64-pc-windows-msvc.zip` | `katara-cli.exe` |

Each archive must have a same-named `.sha256` sidecar. If either asset is missing,
the release is not installable for that platform: stop and report the release gap.
Do not guess another download host, downgrade to a CLI without upload support, or
claim an unexecuted installation succeeded. The supported Linux runtime baseline
is glibc **2.35 or newer** (Ubuntu 22.04 or equivalent), including its normal
`libgcc_s.so.1` runtime. Release CI checks required ELF symbol versions and shared
libraries; these binaries are not statically linked or universal across Linux.
Inspect the host runtime before installation; do not install into older glibc or
an Alpine/musl runtime. Windows ARM64 and other architectures are
not supplied by this release matrix. A source build is a separate explicitly
approved alternative described in the CLI README.

For Linux/macOS, this example uses an already available authenticated or public
GitHub CLI (`gh`) for download. If `gh` is absent, use the host's supported HTTPS
file-download tools on the same official release assets; do not install `gh` as an
unrequested prerequisite or pipe a remote script into a shell. Run installation in
a temporary shell, not by sourcing this block into the user's interactive shell:

```sh
set -eu
repo=katara-ai-inc/katara-cli
case "$(uname -s):$(uname -m)" in
  Linux:x86_64) target=x86_64-unknown-linux-gnu ;;
  Linux:aarch64|Linux:arm64) target=aarch64-unknown-linux-gnu ;;
  Darwin:x86_64) target=x86_64-apple-darwin ;;
  Darwin:arm64) target=aarch64-apple-darwin ;;
  *) printf '%s\n' 'No supported binary for this host.' >&2; exit 1 ;;
esac
asset="katara-cli-${target}.tar.gz"
tag="$(gh release view --repo "$repo" --json tagName --jq .tagName)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
# Fails closed when either asset is absent; no credentials are embedded here.
gh release download "$tag" --repo "$repo" \
  --pattern "$asset" --pattern "$asset.sha256" --dir "$tmp"
(
  cd "$tmp"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum -c "$asset.sha256"
  else
    shasum -a 256 -c "$asset.sha256"
  fi
  test "$(tar -tzf "$asset")" = katara-cli
  tar -xzf "$asset"
  ./katara-cli document upload --help
)
dest="$HOME/.local/bin/katara-cli"
if [ -e "$dest" ] || [ -L "$dest" ]; then
  printf '%s\n' 'Existing installation: review an upgrade separately.' >&2
  exit 1
fi
mkdir -p "$HOME/.local/bin"
install -m 0755 "$tmp/katara-cli" "$dest"
"$dest" --help
```

Installation into `~/.local/bin` does **not** put it on PATH. After the temporary
installer shell exits, either use `$HOME/.local/bin/katara-cli` for every subsequent
command (including login), or run this in the same working shell that will perform
authentication and uploads:

```sh
export PATH="$HOME/.local/bin:$PATH"
command -v katara-cli
katara-cli document upload --help
```

This changes only that shell's environment, not shell startup files. If the host's
execution tools create a fresh shell for each call, use the installed absolute path
on every call or set PATH explicitly for each child process. Do not claim persistent
PATH configuration. The bare `katara-cli` commands below assume command resolution
has been verified; otherwise replace them with the installed absolute path.

For Windows x64, download the ZIP and matching sidecar from one exact tag with
`gh release download`, or through the official Releases page. In PowerShell, verify
with `Get-FileHash -Algorithm SHA256` before `Expand-Archive`; for example, from the
download directory:

```powershell
$asset = 'katara-cli-x86_64-pc-windows-msvc.zip'
$checksum = [IO.File]::ReadAllText((Join-Path $PWD "$asset.sha256"))
if ($checksum -notmatch '\A(?<digest>[a-fA-F0-9]{64})  katara-cli-x86_64-pc-windows-msvc\.zip\r?\n?\z') {
    throw 'Malformed checksum or unexpected archive name'
}
$expected = $Matches['digest']
if ((Get-FileHash $asset -Algorithm SHA256).Hash -ine $expected) {
    throw 'Checksum mismatch; do not install'
}
```

Inspect that the ZIP contains only `katara-cli.exe`, extract into a private temporary
directory, and run that binary's `document upload --help`. After successful checks,
copy it into an approved user-writable directory, such as
`$env:LOCALAPPDATA\Katara\bin`, without overwriting another installation. Invoke
that full path or add it to the current process PATH. Persistent PATH changes and
administrator privileges are separate decisions, not installation defaults.

Report the actual selected release, platform, installed path, checksum result and
help-check result. A checksum verifies agreement with the release publisher's
sidecar; do not call it independent signing/provenance verification. Do not send any
Katara API key during download or help checks.

## 2. User: create a new API key in Katara

The **user**, not the assistant, creates and reviews their credential in the browser:

1. Open [Katara](https://app.katara.ai/), sign in and select the intended organization.
2. Open the organization menu → **API access grants**, or the
   [API Access Grants tab](https://app.katara.ai/dashboard/organization?organizationView=tokens).
3. Choose **Create a new access grant**. Enter a recognizable name and optional
   description for this CLI integration.
4. Remove the default **Website widget answer** preset. For upload plus readback
   and agent listing, select **Document write**, **Document read**, and **Agent read**.
   Review the broader Document write permissions below before accepting.
5. Leave **Allowed browser origins** blank for this CLI/server-side use. Do not
   change an existing browser credential's origin restrictions to repurpose it.
6. Submit the form. The creation flow issues a JWT shown in **JWT Token**. Copy it
   directly to the local CLI's hidden prompt or an approved secret manager, not to
   chat, a skill file, a repository, a shell command argument, or a screenshot.

If the user cannot view/create/issue access grants, ask the organization owner to
arrange the supported user capabilities. Key-management eligibility is separate
from uploading. Do not create a shared administrator key or grant the application
organization-admin authority as a workaround.

### Permissions for this workflow

| Operation | API permission | Dashboard preset |
| --- | --- | --- |
| `document upload` | `create:document` | Document write |
| `document get` (readback) | `read:document` | Document read |
| `document list` | `list:document` | Document read |
| `agent get` | `read:agent` | Agent read |
| `agent list` | `list:agent` | Agent read |

The five permissions above describe the operations, not five independently
selectable dashboard toggles. The current **Document write** preset also includes
`update:document` and `delete:document`: selecting the three presets grants **seven**
permissions. Disclose that difference and let the user decide. If their policy
requires create-only document writes, ask for a supported narrowly provisioned
permission set; do not pretend the dashboard preset is create-only. **Agent run**,
Wiki/memory presets and organization-management permissions are not needed here.

Credential permissions are ceilings, not new resource grants. A Brain upload also
requires an active organization member as the grant owner, current Brain ownership
or Team Brain editor access, and a ready/enabled Brain/project. Viewer-only access
is insufficient; organization administrator status alone is not a Brain role.
Readback requires the owner's current access to that document or Brain. Do not
promise that every Content Uploader document becomes owned by the key creator.

Agent listing remains a server-authorized view, not every Brain/collection in the
organization. Application keys cannot inspect Brain configuration through general
`agent get`; a list may omit restricted Brain entries. On some deployments, even
ordinary agent list/get may still be denied despite Agent read. Report the exact
operation and sanitized denial for the service owner rather than adding admin
permissions or treating a successful upload as proof that agent discovery works.
An explicit user-supplied upload target does not require general agent inspection.

## 3. Authenticate locally; prove reads separately

Have the user run the installed binary's hidden login prompt:

```sh
katara-cli auth login
katara-cli auth list
```

`auth list` masks stored keys. The CLI currently stores its key in a local auth JSON
file (0600 on Unix); it is not an OS keychain. If an approved host secret facility
already supplies `KATARA_API_KEY`, it is consumed by **auth login**, not by ordinary
API commands. Do not ask the user to paste that environment variable's value into
chat, print it, or place a literal key in shell history.

Production defaults to `https://api.katara.ai`. Use only the API endpoint selected
by the user and matching the key's environment. `auth login --api-url` does not
persist endpoint selection: set `KATARA_API_URL` for subsequent calls or pass
`--api-url` to each API command. Use a separate `KATARA_AUTH_FILE` per environment
before login so staging does not replace a production credential. Do not weaken
HTTPS or reuse a browser OAuth access token as the API key.

With the user's explicit organization ID, test discovery independently:

```sh
katara-cli agent list --org-id <org-id>
```

Select only an agent the user intends. If several are returned, ask for the target;
never pick the first. If Brain inspection/discovery is denied, the user can obtain
the exact destination ID from the [Brains dashboard](https://app.katara.ai/dashboard/brain)
or [Agent Library](https://app.katara.ai/dashboard/ai-workflows?aiWorkflowsView=agentsList).
Do not substitute a Q&A alias, collection ID or document ID for the Brain/Content
Uploader agent ID. Preserve an already supplied target on denial.

## 4. Upload only the approved file and destination

Confirm file, organization, agent and intended audience before uploading. An
explicit request with those details can be sufficient; do not scan the workspace,
bulk-upload other files, create an agent, or change sharing as a side effect.
Start with one small non-sensitive file for onboarding. Files must be nonempty and
at most 20 MiB. The synchronous Content Uploader route supports text/Markdown;
Brain binary-format conversion depends on configured server providers.

```sh
katara-cli document upload \
  --org-id <org-id> \
  --agent-id <brain-or-content-uploader-agent-id> \
  --file ./approved-example.txt \
  --content-type text/plain \
  --source-id <stable-external-source-id> \
  --idempotency-key <stable-key-for-this-brain-upload-intent>
```

`--content-type`, `--source-id`, `--idempotency-key`, `--language` and repeated
`--tag-id` are optional. The API defaults source ID to the filename. Ingestion source
IDs are not MCP Q&A aliases. An idempotency key is for retrying the **same Brain
upload intent**, not permission to blindly retry any upload type or change its
arguments. Retain the key, file and metadata when the response is uncertain; do not
create a new intent to work around that uncertainty.

The command prints a document ID. Verify that exact ID, without modifying content:

```sh
katara-cli document get --org-id <org-id> --id <returned-document-id>
```

The CLI prints a bounded single-line preview, not a full-file dump. Verify the
returned document/organization identity and expected preview. If readback is denied,
preserve the upload ID and report acceptance separately from read verification;
do not claim the upload failed and resend it. Ingestion, indexing and Wiki freshness
are different milestones. CLI discovery is not a complete collection inventory.
