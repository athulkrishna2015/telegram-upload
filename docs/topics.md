# Folder trees to forum topics

Turn a directory hierarchy into forum topics. The destination group must have forum topics enabled.

## The two modes

* `-t <directory>` alone: one topic named after the directory; everything inside uploads there recursively.
* `-t <directory> --topic-depth N`: the tree defines the layout —
  * files directly inside the source go to **General**,
  * every non-empty folder at relative depth `1..N` becomes a topic,
  * deeper folders stay in their nearest topic as posted + pinned `📂` announcements,
  * empty folders never create topics.

Level-1 topics use the folder name (`CHEMISTRY`). Nested topics use their relative path (`CHEMISTRY / INTRODUCTION`)
so identical folder names under different parents cannot collide.

## Example

```text
course/
├── index.pdf
└── CHEMISTRY/
    ├── overview.mp4
    └── INTRODUCTION/
        └── lesson.mp4
```

| Command | Result |
|---|---|
| `-t course` | One topic `course` with all files; `CHEMISTRY`, `INTRODUCTION` pinned there |
| `--topic-depth 1` | `index.pdf` → General; videos → topic `CHEMISTRY`; `INTRODUCTION` pinned in it |
| `--topic-depth 2` | `index.pdf` → General; `overview.mp4` → `CHEMISTRY`; `lesson.mp4` → topic `CHEMISTRY / INTRODUCTION` |

## Recommended workflow

```console
# 1. Preview (read-only: no topics created, nothing sent)
$ telegram-upload --to my_group -t "/data/course" --topic-depth 1 --sort --skip --dry-run

# 2. Run it
$ telegram-upload --to my_group -t "/data/course" --topic-depth 1 --sort --skip
```

Sample preview output:

```text
[dry-run] to my_group General: 1 to upload (1024 bytes), 0 skipped, 0 announcements
[dry-run] to my_group topic "CHEMISTRY" (would create): 2 to upload (12345 bytes), 0 skipped, 1 announcements
[dry-run]   upload /data/course/CHEMISTRY/overview.mp4 (12000 bytes)
[dry-run]   announce+pin 📂 INTRODUCTION
```

## Notes and limits

* `--topic-depth` must be ≥ 1. Existing topics are reused (titles match exactly); missing ones are created on real
  runs only.
* Plain `--skip` uses Telegram destination history. Add `--upload-log` to opt into a local cache at
  `<source-folder>/.telegram-upload-log.json`, or `--upload-log-file PATH` to choose the cache file explicitly.
* Local mode is fast and does not scan Telegram history. It records successful uploads made while local mode is
  enabled; it cannot automatically detect earlier uploads or manual deletions from Telegram. The cache is scoped
  by destination/topic/name/size and the reserved cache filename is excluded from recursive uploads.
* `--skip` does not deduplicate `📂` announcements: a rerun may re-pin a heading while skipping its files.
* Interrupted files resume from saved parts on rerun; keep the same source paths.
* The account needs permission to send media, create topics, and pin messages for the full layout to appear as
  planned. See [Troubleshooting](troubleshooting.md).
