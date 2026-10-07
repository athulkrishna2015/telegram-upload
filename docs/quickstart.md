# Quick start

## Authenticate once

You need a personal Telegram account plus an **App `api_id` and `api_hash`** (create them at
[my.telegram.org](https://my.telegram.org/)). Bot tokens do not work with this tool (bot uploads are capped at
50 MB). The first run interactively asks for your phone number, `api_id`, and `api_hash`; credentials are stored per
[Configuration](configuration.md).

## Upload files

Without a destination, files go to your Saved Messages:

```console
$ telegram-upload file1.mp4 file2.mkv
```

Send to a group, channel, or user with `--to`:

```console
$ telegram-upload --to my_group video.mkv
```

## Preview before a big upload

For folder uploads, always preview first with `--dry-run` (nothing is sent and no topics are created):

```console
$ telegram-upload --to my_group -t "/data/course" --topic-depth 1 --sort --skip --dry-run
```

When the plan looks right, run the same command without `--dry-run`.

## Download files

Fetch recent file messages from Saved Messages (default) or another chat:

```console
$ telegram-download
$ telegram-download --from my_group
```

A download-queue pattern: forward files to Saved Messages, then download with `--delete-on-success` so each
message is removed after a successful download.

## Interactive mode

`--interactive` (or `-i`) opens a terminal wizard (mouse supported) to pick files and the destination chat:

```console
$ telegram-upload --interactive
$ telegram-download --interactive
```

Next: [Usage reference](usage.md).
