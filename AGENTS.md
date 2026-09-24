# Project Instructions

## Development

- Use `uv` for Python environments, installs, and commands. Do not use `pip`, `pip3`, or `python -m pip`.
- Run the test suite with:

  ```console
  $ uv run --isolated --python 3.11 --with-requirements requirements-dev.txt python -m unittest discover
  $ git diff --check
  ```

- Keep upload and download changes covered by the smallest relevant unit test.
- Do not commit or push unless explicitly requested.

## Installation and execution

Install the local checkout as a separate step before running it:

```console
$ uv tool install --python 3.11 --force .
```

Run the installed command only after installation succeeds:

```console
$ telegram-upload [OPTIONS] [FILES]...
$ telegram-download [OPTIONS]
```

Do not combine installation and an upload in one shell command. This makes a failed build distinguishable from a failed Telegram operation.

## Live Telegram verification

The project uses Telethon. Use the repository's `TelegramManagerClient` for live checks; do not add Pyrogram or another Telegram client just for verification.

### Safety rules

- Never print or copy `api_hash`, phone numbers, session strings, or session-file contents.
- Use a disposable test album in Saved Messages by default. Do not delete or modify existing user messages.
- Use a real destination only when the user explicitly authorizes the upload.
- Record the message IDs created by a live test and delete only those IDs during cleanup.
- Treat Telegram RPC errors as verification failures; do not claim success from local logs alone.

### Inspect messages

Use the installed configuration and Telethon client to inspect a destination. Replace `CHAT_ID`, `START_ID`, and `END_ID` with the requested values:

```console
$ uv run --isolated --python 3.11 --with-requirements requirements.txt python -c "from telegram_upload.client import TelegramManagerClient; from telegram_upload.config import default_config; c=TelegramManagerClient(default_config()); c.start(); entity=CHAT_ID; ids=list(range(START_ID, END_ID)); [print(m.id, 'grouped_id=', m.grouped_id, 'media=', type(m.media).__name__ if m.media else None, 'caption=', repr(m.text or ''), 'reply_to=', m.reply_to) for m in c.get_messages(entity, ids=ids) if m]"
```

For album verification, `grouped_id` must be the same non-`None` value for every item in an album. `text` is the per-item caption. For forum-topic verification, also inspect `m.reply_to` and confirm the topic reply metadata.

### Verify a disposable album

1. Create two or three tiny image files in `/tmp`.
2. Start `TelegramManagerClient(default_config())` with `client.start()`.
3. Record the newest Saved Messages ID before uploading.
4. Call `client.send_files_as_album('me', files)` using `telegram_upload.upload_files.File` objects.
5. Fetch messages newer than the recorded ID with `client.get_messages('me', min_id=oldest_id)`.
6. Assert that all expected items have one shared non-`None` `grouped_id` and that each caption equals its full filename.
7. Delete only the newly created message IDs with `client.delete_messages('me', ids)`.

A successful local test suite is necessary but does not replace this live check: Telegram can reject media, forum replies, or album grouping even when mocks pass.

### Verify an upload or rerun

Use `--skip` for reruns. It compares the destination's existing filename and size; it does not rely on a local duplicate database. Resume state is stored separately in `~/.config/telegram-upload-progress.json` and is for interrupted individual uploads, not completed-file deduplication.

After a live run, inspect the destination messages with the inspection command above. Confirm expected filenames, captions, topic placement, and `grouped_id` before reporting completion.
