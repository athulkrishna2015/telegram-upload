# Architecture

This page describes how the current checkout routes local files to Telegram, with emphasis on forum-topic folder uploads, dry-run planning, duplicate skipping, and interrupted-upload resume.

## High-level flow

```text
CLI arguments
    │
    ▼
management.upload
    ├── resolve destinations and topic plan
    ├── expand directory trees into files + DirectoryMarker values
    ├── prepare File / SplitFile upload objects
    ├── dry-run: classify and report, or
    └── real run: send_files / send_files_as_album
              │
              ▼
       TelegramUploadClient
         ├── optional history scan for --skip
         ├── emit and pin folder announcements
         ├── upload media and message into a chat/topic
         └── persist/resume individual file parts
```

The command has a planning phase and an execution phase. Topic-folder expansion happens before sending, so a single input tree can become multiple destination groups. Each group then has one chat entity, an optional forum root message ID, and a sequence of prepared items.

### Phase boundaries

| Phase | Main owner | Local/remote effects |
|---|---|---|
| Parse CLI and pair destinations | `management.upload` | Local only. Invalid argument combinations stop here. |
| Expand paths and validate files | `management.upload`, `upload_files.py` | Reads local directory entries and file metadata. |
| Resolve forum topics | `TelegramManagerClient` | Read-only topic lookup; real mode may create missing topics. |
| Plan actions | `plan_files` | Reads cached or fetched destination history only when `--skip` is requested. |
| Transfer and send | `TelegramUploadClient` | Uploads parts, sends media/messages, and attempts to pin folder markers. |
| Persist transfer progress | `ProgressManager` | Writes local JSON progress state during part transfers. |

This distinction matters when interpreting `--dry-run`: it disables the transfer/send phase, not all network activity or local reads.

```text
source directory
  ├── depth 0 files ───────────────────────────────► General
  ├── depth 1 directory ─► topic "CHEMISTRY"
  │     ├── files ─────────────────────────────────► CHEMISTRY
  │     └── depth 2 directory ─► topic at depth 2
  │           └── depth > N directory ─► pinned 📂 marker
  │                 └── files ────────────────────► nearest topic
  └── empty topic-level directory ─────────────────► ignored
```

The application uses the user's Telegram account through Telethon. The main layers are:

| Module | Responsibility |
|---|---|
| `telegram_upload/management.py` | Click CLI options, destination/topic pairing, directory-to-topic planning, upload orchestration, dry-run output. |
| `telegram_upload/upload_files.py` | Directory traversal, `DirectoryMarker`, file metadata/captions/thumbnails, and `File`/`SplitFile` wrappers. |
| `telegram_upload/client/telegram_manager_client.py` | Configuration-backed Telethon client, topic lookup/creation, file size limits, and upload/download client composition. |
| `telegram_upload/client/telegram_upload_client.py` | File/media sending, topic replies, pinned folder announcements, skip planning, chunk upload, and progress persistence. |
| `telegram_upload/client/telegram_download_client.py` | Message/file discovery and download behavior. |

### Important data types

| Type | Purpose |
|---|---|
| `DirectoryMarker` | Represents a directory boundary in the recursive stream; it is not a file and is used to create a folder announcement. |
| `File` | Reopenable file stream wrapper carrying path, filename, size, caption, thumbnail, and media attributes. |
| `SplitFile` | A bounded view of a large source file used for `--large-files split`; each view maps to a separately sent Telegram file. |
| Destination tuple `(entity, reply_to)` | Chat/channel entity plus optional forum topic root message ID. `None` means General/main chat. |

### Important methods

| Method | Role |
|---|---|
| `management.upload` | CLI entry point. Expands topic-depth trees and dispatches destination groups. |
| `TelegramManagerClient.find_topic` | Searches for a matching title without creating it. |
| `TelegramManagerClient.get_or_create_topic` | Reuses a matching title or requests a new forum topic. |
| `TelegramUploadClient.plan_files` | Returns action/file pairs for upload, skip, announcement, or ignored marker. |
| `TelegramUploadClient.send_files` | Executes the plan for ordinary individual sends. |
| `TelegramUploadClient.send_files_as_album` | Stages media and sends resilient batches of up to ten items. |
| `TelegramUploadClient.upload_file` | Uploads the actual bytes in Telegram-sized parts and records successful parts. |
| `ProgressManager` | Loads, updates, and removes local per-file upload progress records. |

## Upload planning and execution

`management.upload` first parses `--to`, `--topic`, and positional file arguments into destination groups. Repeated `--to` and `--topic` values are paired according to the CLI's documented pairing rules; in explicit multi-topic mode, files are associated with topic markers in argument order. It then validates paths and applies directory and large-file policies:

1. Directory traversal yields ordinary paths plus `DirectoryMarker` objects for discovered folders.
2. Large-file handling wraps paths as `File` objects or yields `SplitFile` parts when `--large-files split` is selected.
3. Optional sorting is applied to the prepared stream.
4. Each destination group is sent by `TelegramUploadClient.send_files`; `--album` uses `send_files_as_album`, which stages media and then sends batches of up to ten items.

The parent CLI constructs groups as lists before sending them. Consequently, a multi-destination upload may retain prepared file wrappers until all groups have been collected. When the same wrapper is used more than once, the CLI resets its stream position before the subsequent destination send.

`File` wraps a local path with its filename, size, caption, optional thumbnail, and Telegram media attributes. Unless `--force-file` is used, media is sent using MIME/metadata information. Recognized video files receive video attributes; supported MP4 metadata marks the video as streamable.

### Example expansion

Given this source:

```text
Library/
├── catalog.pdf
└── SCIENCE/
    ├── intro.mp4
    └── CHEMISTRY/
        ├── lesson.pdf
        └── LABS/
            └── setup.mp4
```

The destination grouping is:

| Invocation | General | Forum topics | Pinned folder markers |
|---|---|---|---|
| `-t Library` (no `--topic-depth`) | — | `Library` receives the entire tree | `SCIENCE`, `CHEMISTRY`, `LABS` in `Library` |
| `-t Library --topic-depth 1` | `catalog.pdf` | `SCIENCE` receives all files below it | `CHEMISTRY`, `LABS` in `SCIENCE` |
| `-t Library --topic-depth 2` | `catalog.pdf` | `SCIENCE`; `SCIENCE / CHEMISTRY` | `LABS` in `SCIENCE / CHEMISTRY` |
| `-t Library --topic-depth 3` | `catalog.pdf` | `SCIENCE`; `SCIENCE / CHEMISTRY`; `SCIENCE / CHEMISTRY / LABS` | — |

Use `--dry-run` with the same options to inspect which folders are treated as topics and which become pinned markers before making remote changes.

## Folder depth and forum topics

The default `-t <directory>` behavior uses the directory's basename as one topic and recursively uploads that directory's contents there. Directories below it are represented as `DirectoryMarker`s and normally become pinned `📂` messages. Root files are also sent to that one topic.

`--topic-depth N` activates hierarchy splitting for a directory passed as the topic source:

* Source-root files are assigned to General (no `reply_to` topic ID).
* Every non-empty descendant folder at relative depth `1..N` becomes a topic.
* Level-1 topic titles are the folder names. Nested topic titles use a slash-separated relative path, for example `CHEMISTRY / INTRODUCTION`.
* Descendant folders deeper than `N` remain within the nearest ancestor topic and are emitted as `DirectoryMarker`s. The uploader posts and attempts to pin each marker; files below it remain in that topic.
* Empty topic-level directories do not create topics.

The current implementation scans and sorts each directory's immediate entries before expansion. It does not follow symlinked directory trees as regular subdirectories. A tree may change between planning and upload; dry-run output is not a locked snapshot.

### Topic tree worked example

For the tree below:

```text
Root/
├── index.pdf
└── A/
    ├── a.txt
    └── B/
        ├── b.txt
        └── C/
            └── c.txt
```

At depth 2, the expansion produces three destination groups:

```text
General                 index.pdf
topic "A"               a.txt
topic "A / B"           b.txt, 📂 C, c.txt
```

The marker appears before the contents of that deeper directory. This preserves the traversal order so the pinned folder heading precedes its files in the topic history.

Topic resolution is performed by `TelegramManagerClient.find_topic` and `get_or_create_topic`. Existing titles are reused. A real run creates missing topics; a dry run only searches and labels them as would-create. Telegram permissions and forum-group requirements are enforced remotely, so local planning cannot guarantee that the eventual RPC will succeed.

## Dry-run architecture and limits

`--dry-run` uses the same path expansion and topic grouping as an upload, then reports file actions rather than calling send/pin/upload operations. It can perform read-only Telegram requests to resolve the chat, look up topics, and—with `--skip`—read destination history.

Dry-run does not:

* create forum topics;
* send or pin folder announcements;
* upload file bytes or send media/messages;
* delete local files.

For a topic that would be newly created, there is no topic history to scan, so the planner lists its files as uploads even with `--skip`. Dry-run is an estimate of the local plan; Telegram can still reject a file, topic title, permission, or upload when a real run is attempted.

Folder expansion and basic path/size validation still run locally. Thumbnail generation and some media metadata extraction may be deferred until actual sending, so dry-run is not a full media decode or Telegram acceptance test. The selected files can also change after the preview.

The shared `TelegramUploadClient.plan_files` method classifies prepared items as upload, skip, announce, or ignored. The send path consumes this plan too, so skip matching rules are shared with dry-run rather than implemented independently.

The plan categories mean:

| Action | Meaning |
|---|---|
| `upload` | A `File`/`SplitFile` would be sent as an individual message, or staged for an album. |
| `skip` | Existing destination history matched the local item's name/size or supported caption fallback. |
| `announce` | A directory boundary would create a `📂` message; a live send attempts to pin it. |
| `ignored` | A marker has no separate message in the selected send mode (for example, album handling). |

## Skip matching

With `--skip`, `_get_upload_history` loads media messages from the target chat/topic and caches the result for that destination during the client run. `plan_files` checks documents by filename and size and by caption/size fallback; photos can match by caption filename or stem. It does not hash local and remote bytes. Same-name, same-size content changes can therefore be treated as duplicates.

Skip does not currently deduplicate directory announcements. On a rerun, files may be skipped while folder announcements are sent again. For a tree split into many topics, history is checked separately per destination topic.

The history cache is scoped by chat and topic for the lifetime of the client process. Messages that arrive after the cache is fetched during the current run may not be reflected in a subsequent plan for that same destination.

The destination and topic selection matter: run with the same `--to` and topic mapping to compare against the same history. Skip is a completed-file deduplication check; it is separate from upload-part resume.

## Interrupted-upload resume

For each uploaded file, the upload client calculates a stable local key using its absolute path and size. `ProgressManager` persists the Telegram file ID and completed chunk indexes to `~/.config/telegram-upload-progress.json`. On rerun with the same path and size, completed parts can be reused. Progress is removed after successful completion.

The upload implementation sends file parts concurrently, bounded by `TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS`. A part is marked complete after the corresponding Telegram part request succeeds, and the progress record is rewritten as progress advances. Resume therefore concerns the transfer of bytes to Telegram's temporary uploaded-file handle; it is not a remote message-level transaction.

Telegram distinguishes transferring a file to its upload service from sending a message that references that upload. If the process stops after all parts transfer but before Telegram accepts the final media message, the local progress may already be removed or the send may need to be retried. Inspect the destination before manually retrying without `--skip` if avoiding duplicate messages is important.

Resume applies to the individual file whose transfer was interrupted. It does not prevent completed files earlier in the command from being sent again. Add `--skip` for completed-file detection when rerunning a larger job. Moving or renaming the local file can prevent its resume key from matching.

## Topic messages and pinning

For a topic upload, media and folder announcements use Telegram reply metadata pointing at the topic root. A `DirectoryMarker` produces a `📂 **folder-name**` message and the client attempts to pin that message. Pin failures caused by Telegram permissions are intentionally caught, so an announcement may be present without being pinned. Ordinary files are not explicitly pinned by the uploader.

Forum operations have remote prerequisites: the destination must be a forum-enabled group; the account must be able to view it, send media, create topics (when needed), and pin announcements if pinned markers are required. These permissions are not fully knowable from the local planner.

The uploader catches RPC failures when pinning a marker so that a permission failure does not abort every later file. Therefore a successful file transfer does not imply every folder announcement was pinned. Other RPC failures during file/topic operations can be retried or surfaced depending on the operation.

## Failure and retry boundaries

* Upload part network failures are retried by the upload client; completed part indexes are persisted for later runs.
* Flood waits are honored by sleeping for Telegram's requested interval before retrying the file send.
* File-send RPC failures are retried a bounded number of times by `send_one_file`; a final failed file is reported, and later files can continue.
* Topic creation failures are reported and may leave the topic ID unresolved; verify the resulting Telegram placement rather than treating local output as proof.
* Pinning failure is non-fatal and may leave the folder message unpinned.
* Album batches rejected by Telegram are retried as smaller batches; invalid individual items can be skipped.

Because these operations are not one atomic transaction, a command can partially succeed. A rerun with the same destination mapping plus `--skip` is the normal recovery path for completed files, while resume state handles the currently interrupted file transfer.

## State and side-effect map

| State/action | Location | Lifetime/cleanup |
|---|---|---|
| API configuration | `~/.config/telegram-upload.json` | Persistent credentials/configuration. Protect it. |
| Telethon session | `~/.config/telegram-upload.session` | Persistent authenticated session. Do not publish or copy insecurely. |
| Upload part progress | `~/.config/telegram-upload-progress.json` | Updated during upload; per-file entry removed after completion. |
| Skip history cache | In-memory client field, keyed by chat/topic | Exists only for the current process. |
| Forum topics, messages, pins | Telegram | Persistent remote side effects; dry-run avoids mutation. |

`TELEGRAM_UPLOAD_CONFIG_DIRECTORY` controls configuration/session paths. In the current upload client, the progress JSON path is separately constructed from the default `CONFIG_DIRECTORY` constant, so verify the installed version before assuming a custom config directory relocates progress state.

## Operational scenarios

### Preview a topic tree

```console
$ telegram-upload --to my_group -t /data/Library --topic-depth 2 --sort --skip --dry-run
```

This resolves the group, looks for existing topic titles, checks history for existing topics due to `--skip`, and prints a plan. Newly missing topics are labeled as would-create; no upload starts.

### Start or rerun a large tree upload

```console
$ telegram-upload --to my_group -t /data/Library --topic-depth 2 --sort --skip
```

If interrupted, rerun the same command while the source paths remain unchanged. The in-progress file resumes from saved parts; completed messages are considered by `--skip`. Without `--skip`, files completed before interruption may be sent again.

### Change the topic mapping

Changing `--topic-depth`, source root, or topic titles changes destination selection. Review with `--dry-run` first. `--skip` only checks the destination selected by the current mapping, so moving a file to a new topic does not make the old topic's message count as a duplicate in the new topic.

## Tests and verification

Unit tests live under `tests/`; topic planning and CLI behavior are covered primarily by `tests/test_management.py`, while upload client logic is covered by `tests/test_client/test_telegram_upload_client.py`.

When changing planning behavior, prefer tests that assert the destination grouping and ordered item stream (files versus `DirectoryMarker`s), along with a dry-run test asserting that send/create/pin methods are not called. When changing Telegram sends, test the relevant message reply metadata and media attributes in the upload-client tests.

Run the suite using the repository instructions:

```console
$ uv run --isolated --python 3.11 --with-requirements requirements-dev.txt python -m unittest discover
$ git diff --check
```

Mocks validate local routing and request construction. For a real Telegram integration check, use a disposable destination, inspect resulting message IDs/topic reply metadata and media attributes, and clean up only messages created by that test.

## See also

* [Usage](usage.md) — CLI workflows, forum-topic folder mapping, and dry-run examples.
* [Installation](installation.md) — installing this checkout with the documented options.
* [Troubleshooting](troubleshooting.md) — diagnosing failed uploads, resume, and rate limits.
