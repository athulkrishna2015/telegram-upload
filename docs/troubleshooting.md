# Troubleshooting

This guide covers common installation, authentication, forum-topic, upload, resume, and performance issues.

## Start with a safe diagnosis

1. Check which executable is installed and which options it supports:

   ```console
   $ which telegram-upload
   $ telegram-upload --help
   ```

2. If using checkout-specific options such as `--topic-depth` or `--dry-run`, reinstall the checkout as described in [Installation](installation.md).
3. For a large or recursive job, run the exact command with `--dry-run` first.
4. Check the destination in Telegram after any partial failure; the CLI may have completed some files before a later file failed.
5. Protect configuration/session files and redact API credentials, phone numbers, session strings, and private links from logs or support requests.

## The CLI says an option does not exist

The stable PyPI release or an older local installation may not include this checkout's `--topic-depth` or `--dry-run` options. Install this repository checkout from its root:

```console
$ uv tool install --python 3.11 --force .
$ telegram-upload --help
```

Confirm that help lists the desired option before starting an upload. When multiple installations exist, `which telegram-upload` reveals which executable your shell selected.

## Topic creation or placement fails

Forum topic uploads require a forum-enabled supergroup. Check that:

* `--to` resolves to the intended group, not a similarly named channel or chat;
* the account can access the group and send messages/media;
* the account can create topics if the requested title does not already exist;
* topic titles are spelled as intended. Existing title matching is exact;
* numeric topic IDs belong to that group.

Use a dry run to see the resolved destination and whether a named topic exists or would be created:

```console
$ telegram-upload --to my_group -t "/data/Library" --topic-depth 1 --dry-run
```

A dry run performs read-only Telegram lookups, but it cannot guarantee the later create/send permission or predict every RPC failure. A warning about an unknown numeric topic ID means files may land in General if the Telegram API cannot route them to that topic.

## Folder tree maps to the wrong topic layout

Without `--topic-depth`, a directory provided to `-t` becomes one topic named after that directory; all files and subfolders are uploaded into it. Use `--topic-depth N` to make folders below the source into topics:

```console
$ telegram-upload --to my_group -t "/data/Library" --topic-depth 1 --dry-run
```

At depth 1, source-root files go to General, immediate folders become topics, and deeper folders become pinned folder announcements inside their nearest topic. At depth 2, the first two folder levels become topics; nested topic names include their parent path, for example `SCIENCE / CHEMISTRY`.

Review the dry-run output before a real upload. In particular, confirm root-level files are assigned to General and each category folder resolves to the topic you expect.

## Some folder announcements are not pinned

The uploader sends a `📂` message for directory markers and attempts to pin it. Telegram may refuse to pin because of group permissions or settings. Pinning errors are intentionally non-fatal, so files can continue uploading while the heading remains unpinned. Grant the account permission to pin messages and pin the heading manually if needed.

With `--skip`, file deduplication does not deduplicate directory announcements. A rerun may skip existing files but send/pin the folder heading again.

## Upload was interrupted; how do I continue?

For an interrupted individual file, rerun the same command with the same source path and destination. Uploaded parts are recorded in `~/.config/telegram-upload-progress.json` and reused where possible. The in-progress entry is removed after completion.

Completed files earlier in the command are not automatically suppressed. Add `--skip` to avoid re-uploading completed messages:

```console
$ telegram-upload --to my_group -t "/data/Library" --topic-depth 1 --sort --skip
```

Resume state is tied to the absolute local path and size (and its upload file ID is derived using file metadata); moving or renaming a file can prevent resumption. Do not edit the progress JSON while an upload is active. If a run stopped after the bytes transferred but before the message appeared, inspect Telegram before retrying to avoid duplicates.

## `--skip` uploads something I expected it to skip

`--skip` compares remote history in the selected chat/topic. For documents it uses filename and size, with caption/size fallback; photos can match caption filename/stem. It does not hash contents. Therefore:

* use the same `--to` and topic mapping as the original upload;
* a renamed file may not match;
* changed content with the same name and size may incorrectly look like a duplicate;
* photos without a recognizable filename caption may not match as expected;
* newly-created topics have no preexisting history to compare on the first run.

Use `--dry-run --skip` to inspect the decisions before uploading. A dry run may still read Telegram history, but it does not send files.

## Video is sent as a document or cannot stream

Do not use `--force-file` if you want Telegram to recognize the media as a video. The uploader infers media from file type and metadata. Streaming depends on the container and codec support in Telegram, not just the `.mp4` extension. The client may attach streaming metadata for recognized MP4 video; formats such as some MKV files may upload/play differently.

For a compatible MP4 transcode, one possible ffmpeg command is:

```console
$ ffmpeg -i input.mov -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart output.mp4
```

See [Supported file types](supported_file_types.md). Always check the behavior in the Telegram client used by recipients.

## Upload is slow or Telegram returns 429 / FloodWait

Uploads use parallel file parts. Higher concurrency may improve throughput but also increases memory/CPU use and can trigger Telegram rate limits. Reduce parallel blocks first:

```console
$ TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS=2 telegram-upload --to my_group video.mkv
```

The current default is 8 parallel blocks. Additional TCP connections can be configured with `TELEGRAM_UPLOAD_MAX_CONNECTIONS`, but increasing connections may cause more rate limiting. Flood waits should be honored; avoid repeatedly restarting commands to bypass them. See [Upload benchmarks](upload_benchmark.md).

Relevant retry settings include:

| Variable | Default | Purpose |
|---|---:|---|
| `TELEGRAM_UPLOAD_MAX_RECONNECT_RETRIES` | `5` | Reconnect attempts after network failures. |
| `TELEGRAM_UPLOAD_RECONNECT_TIMEOUT` | `5` | Maximum reconnect wait window in seconds. |
| `TELEGRAM_UPLOAD_MIN_RECONNECT_WAIT` | `2` | Base reconnect wait, increased on retries. |

## File is rejected or too large

The user account limit is currently 2 GiB for standard accounts and 4 GiB for Premium accounts. `--large-files split` divides oversized files into separate numbered parts; use `telegram-download --split-files join` when retrieving them. Splitting changes the remote file layout and does not create a single native Telegram file.

Zero-byte files are rejected by local validation. Check available disk space, file readability, and whether files changed while scanning a large directory.

## Database is locked

An existing process may still hold the Telethon session lock. Only one process should use a given session file at a time.

```console
$ pgrep -af telegram-upload
$ fuser ~/.config/telegram-upload.session
```

Stop the stale process normally. If concurrent independent sessions are required, create separate session files/configurations rather than sharing one session file. Do not delete or modify a session file while its process is active.

## Proxy or connection errors

Check the scheme, host, and port in `--proxy`. Supported schemes include `mtproxy`, `http`, `socks4`, and `socks5`; SOCKS/HTTP support may require the optional PySocks dependency. Environment variables are also supported: `TELEGRAM_UPLOAD_PROXY`, `HTTPS_PROXY`, and `HTTP_PROXY` (in that precedence order, with the explicit `--proxy` taking priority).

Try a small Saved Messages upload first to distinguish a destination permission problem from general connectivity. Do not include proxy passwords in pasted logs.

## Installation or dependency errors

Use the repository's recommended Python version and isolated tool installation:

```console
$ uv tool install --python 3.11 --force .
```

When reporting a reproducible issue, include the command with private paths/identifiers redacted, Python version, operating system, package version, and sanitized error traceback. Never attach Telegram session/config files or disclose `api_hash` values.

Before opening a ticket, check the [existing issues](https://github.com/Nekmo/telegram-upload/issues). For project development, run the test suite documented in [Contributing](contributing.md).
