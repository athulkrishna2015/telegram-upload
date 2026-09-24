![logo](https://raw.githubusercontent.com/Nekmo/telegram-upload/master/logo.png)

[![pip-rating badge](https://raw.githubusercontent.com/Nekmo/telegram-upload/pip-rating-badge/pip-rating-badge.svg)](https://github.com/Nekmo/telegram-upload/actions/workflows/pip-rating.yml)
[![Latest Tests CI build status](https://img.shields.io/github/actions/workflow/status/Nekmo/telegram-upload/test.yml?style=flat-square&maxAge=2592000&branch=master)](https://github.com/Nekmo/telegram-upload/actions?query=workflow%3ATests)
[![Latest PyPI version](https://img.shields.io/pypi/v/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Python versions](https://img.shields.io/pypi/pyversions/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/Nekmo/telegram-upload.svg?style=flat-square)](https://codeclimate.com/github/Nekmo/telegram-upload)
[![Test coverage](https://img.shields.io/codecov/c/github/Nekmo/telegram-upload/master.svg?style=flat-square)](https://codecov.io/github/Nekmo/telegram-upload)
[![Github stars](https://img.shields.io/github/stars/Nekmo/telegram-upload?style=flat-square)](https://github.com/Nekmo/telegram-upload)

# telegram-upload

Telegram-upload uses your **personal Telegram account** to **upload** and **download** files up to **4 GiB** (2 GiB for free users). Turn Telegram into your personal ☁ cloud!

To install **this checkout**, including the `-t/--topic` options documented below, run this command from the repository root:

```console
$ uv tool install --python 3.11 --force .
```

Python 3.11 is used because the current code imports `distutils`, which was removed in Python 3.12.

To install the upstream PyPI release instead:

```console
$ uv tool install --python 3.11 telegram-upload
```

> The PyPI release does not currently include this checkout's topic options.

You can also install the upstream master branch from GitHub:

```console
$ uv tool install --python 3.11 https://github.com/Nekmo/telegram-upload/archive/refs/heads/master.zip
```

Alternatively, you can use pip:

```console
$ pip3 install telegram-upload
```

More installation options, including [Docker](#-docker), are available in the [📕 documentation](https://docs.nekmo.org/telegram-upload/installation.html).

![demo](https://raw.githubusercontent.com/Nekmo/telegram-upload/master/telegram-upload-demo.gif)

## ❓ Usage

To use this program you need an Telegram account and your **App api_id & api_hash** (get it in [my.telegram.org](https://my.telegram.org/)). The first time you use telegram-upload it requests your 📱 **telephone**, **api_id** and **api_hash**. Bot tokens can not be used with this program (bot uploads are limited to 50MB).

To **send ⬆️ files** (by default it is uploaded to saved messages):

```console
$ telegram-upload file1.mp4 file2.mkv
```

You can **download ⤵️ the files** again from your saved messages (by default) or from a channel. All files will be downloaded until the last text message.

```console
$ telegram-download
```

[Read the documentation](https://docs.nekmo.org/telegram-upload/usage.html#telegram-download) for more info about the options availables.

### Interactive mode

The **interactive option** (`--interactive`) allows you to choose the dialog and the files to download or upload with a **terminal 🪄 wizard**. It even **supports mouse**!

```console
$ telegram-upload --interactive    # Interactive upload
$ telegram-download --interactive  # Interactive download
```

[More info in the documentation](https://docs.nekmo.org/telegram-upload/usage.html#interactive-mode)

## Tests

To run the unit tests:

```console
$ python3 -m unittest discover tests
```

You can also run functional tests using the provided script (requires a `.env` file or local configuration):

```console
$ ./tests/functional_test.sh
```

### Set group or chat

By default when using telegram-upload without specifying the recipient or sender, telegram-upload will use your personal chat. However you can define the 👨 destination. For file upload the argument is `--to <entity>`. For example:

```console
$ telegram-upload --to telegram.me/joinchat/AAAAAEkk2WdoDrB4-Q8-gg video.mkv
```

You can also upload or download files from a specific **topic** in a forum-enabled group using the `--topic <id_or_name>` (or `-t <id_or_name>`) parameter:

```console
$ telegram-upload --to my_group --topic 42 video.mkv
$ telegram-upload --to my_group --topic "Physics Class" video.mkv
```

If you provide a **directory path** to the topic flag, the tool will automatically create a topic with the folder's name (if it doesn't exist) and upload all files inside that folder to that topic.

However, if you pass a folder as a **positional argument** (without `-t`), it will upload all files inside it to the main chat or the "General" topic. By default folders are processed recursively, but you can also use the `--recursive` (or `-r`) flag explicitly:

```console
# Upload files in folder to the main chat (no topic created)
$ telegram-upload --to my_group "/path/to/Nuclear Physics"
$ telegram-upload --to my_group -r "/path/to/Nuclear Physics"

# Automatically create/find topic "Nuclear Physics" and upload its content there
$ telegram-upload --to my_group -t "/path/to/Nuclear Physics"
```

Telegram-upload supports **multiple destinations** in a single command. You can **distribute** different files to different topics using the `--distribute` flag. This will divide the files among the destinations:

```console
# Send file1.zip to Topic 1 and file2.zip to Topic 2
$ telegram-upload --to my_group -t 1 -t 2 --distribute file1.zip file2.zip
```

For **explicit mapping**, you can repeat the topic flag followed by the specific files for that topic (1-to-1 mapping). Comma-separated lists are also supported. You can even use multiple groups as "buckets" for sets of topics:

```console
# Send file1 to Topic 1 and file2 to Topic 2
$ telegram-upload --to MyGroup -t 1 "file1.zip" -t 2 "file2.zip"

# Multiple folders to different topics
$ telegram-upload --to MyGroup -t "./Folder1" -t "./Folder2"

# Advanced: 2 files to Topic 1 & 2 in Group A, and 2 files to Topic 1 & 2 in Group B
$ telegram-upload --to GroupA -t 1 "file1" -t 2 "file2" --to GroupB -t 1 "file3" -t 2 "file4"

# Multiple files per topic using commas
$ telegram-upload --to MyGroup -t 442 "vid1.mp4,pdf1.pdf" -t 445 "vid2.mp4"
```

You can see all [the possible values for the entity in the documentation](https://docs.nekmo.org/telegram-upload/usage.html#set-recipient-or-sender).

### Performance & Speed

To **improve upload speed**, you can increase the number of parallel upload blocks and use multiple connections (Speed Boost).

* `TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS`: Number of chunks sent in parallel. Default is `8`.
* `TELEGRAM_UPLOAD_MAX_CONNECTIONS`: Number of parallel TCP connections to use. Default is `1`. Increasing this can significantly boost speed for high-bandwidth connections.

```console
# Boost speed using 16 parallel blocks and 4 connections
$ export TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS=16
$ export TELEGRAM_UPLOAD_MAX_CONNECTIONS=4
$ telegram-upload large-file.zip
```

Note: Using too many connections may lead to temporary rate limits (Flood Wait) from Telegram.

### Split & join files

If you try to upload a file that **exceeds the maximum supported** by Telegram by default, an error will occur. But you can enable ✂ **split mode** to upload multiple files:

```console
$ telegram-upload --large-files split large-video.mkv
```

Files split using split can be rejoined on download using:

```console
$ telegram-download --split-files join
```

Find more help in [the telegram-upload documentation](https://docs.nekmo.org/telegram-upload/usage.html#split-files).

### Skip already uploaded

You can **skip ⏭️ files** that have already been uploaded to the destination chat (channel, topic, or group) using the `--skip` (or `-s`) flag. This checks the destination for files with the same name and size:

```console
$ telegram-upload --skip video.mp4
```

### Resume support

Telegram-upload **automatically 🔄 resumes** interrupted uploads for large files. If an upload is stopped due to a network failure or manual interruption, simply run the same command again, and it will pick up from the last successfully uploaded part.

Progress is tracked in `~/.config/telegram-upload-progress.json` and is automatically cleaned up once the upload is complete.

### Network Resilience

The tool is designed to be **resilient to network 🌐 drops**. It will persistently retry connection errors and timeouts, making it suitable for unstable connections or long-running uploads.

### Delete on success

The `--delete-on-success` option allows you to ❌ **delete the Telegram message** after downloading the file. This is useful to send files to download to your saved messages and avoid downloading them again. You can use this option to download files on your computer away from home.

### Configuration

Credentials are saved in `~/.config/telegram-upload.json` and `~/.config/telegram-upload.session`. You must make sure that these files are secured. You can copy these 📁 files to authenticate `telegram-upload` on more machines, but it is advisable to create a session file for each machine.

### Upload albums

The `--album` (or `-a`) flag groups photos and videos into albums of up to **10 items**. Each item gets its own **full filename as caption**:

```console
$ telegram-upload --album -r --skip /path/to/folder
```

Notes:

* Folder `📂` announcements are skipped in album mode.
* Per-item captions are visible when opening a photo individually, not in the album grid (Telegram UI behavior).
* Captions are message text, so in-chat search by filename finds the item.

### Captions

Use `--caption` to override the default caption (the filename without extension). Templates support file variables, for example `{file.stem}`:

```console
$ telegram-upload --caption "Backup {file.stem}" file1.mp4
```

### Full option reference

`telegram-upload [OPTIONS] [FILES]...`

| Option | Description |
|---|---|
| `--to TEXT` | Destination: phone, username, invite link, chat id, or `me` (default). Repeatable. |
| `--config TEXT` | Config file (default `~/.config/telegram-upload.json`). |
| `-d, --delete-on-success` | Delete the local file after a successful upload. |
| `--print-file-id` | Print the uploaded file's id. |
| `--force-file` | Always send as a file (keeps filename, no preview). |
| `-f, --forward TEXT` | Forward each upload to another chat/user. Repeatable. |
| `--directories [fail\|recursive]` | How to handle directories (default `fail`). |
| `-r, --recursive` | Upload directories recursively (sets `--directories recursive`). |
| `--large-files [fail\|split]` | How to handle files over the Telegram limit (default `fail`). |
| `--caption TEXT` | Caption template (supports `{file.*}` variables). Default: filename. |
| `--no-thumbnail` | Disable thumbnail generation (mutually exclusive with `--thumbnail-file`). |
| `--thumbnail-file TEXT` | Custom preview image for uploads. |
| `-p, --proxy TEXT` | `http`, `socks4`, `socks5` or `mtproto` proxy, e.g. `socks5://user:pass@1.2.3.4:8080`. |
| `-a, --album` | Group photos/videos into albums of up to 10, each captioned with its filename. |
| `-i, --interactive` | Terminal wizard to pick files and destination (mouse supported). |
| `--sort` | Sort files by name (natural sort if `natsort` is installed). |
| `-t, --topic TEXT` | Forum topic id, name, or folder path. Repeatable; pairs with `--to` and positional files. |
| `--distribute` | Split files across destinations instead of sending all files everywhere. |
| `-s, --skip` | Skip files whose name and size already exist in the destination. |

`telegram-download [OPTIONS]`

| Option | Description |
|---|---|
| `-f, --from TEXT` | Source: phone, username, chat id, or `me` (default). Repeatable. |
| `--config TEXT` | Config file (default `~/.config/telegram-upload.json`). |
| `-d, --delete-on-success` | Delete the Telegram message after downloading (download queue). |
| `-p, --proxy TEXT` | Same proxy format as upload. |
| `-m, --split-files [keep\|join]` | Rejoin files previously uploaded with `--large-files split` (default `keep`). |
| `-i, --interactive` | Terminal wizard to pick source and files. |
| `-t, --topic TEXT` | Topic id or name to download from. Repeatable. |

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS` | `8` | File chunks uploaded in parallel. |
| `TELEGRAM_UPLOAD_MAX_CONNECTIONS` | `1` | Parallel TCP connections (speed boost; too many can trigger Flood Wait). |
| `TELEGRAM_UPLOAD_MAX_RECONNECT_RETRIES` | `5` | Reconnect attempts on connection errors. |
| `TELEGRAM_UPLOAD_RECONNECT_TIMEOUT` | `5` | Timeout between reconnect attempts. |
| `TELEGRAM_UPLOAD_MIN_RECONNECT_WAIT` | `2` | Minimum wait before retrying a failed part. |
| `TELEGRAM_UPLOAD_PARALLEL_DOWNLOAD_BLOCKS` | `10` | Download chunks fetched in parallel. |
| `TELEGRAM_UPLOAD_PROXY` (`HTTPS_PROXY`, `HTTP_PROXY`) | — | Proxy fallback chain. |
| `TELEGRAM_UPLOAD_SESSION` | — | Session string override (instead of the session file). |
| `TELEGRAM_UPLOAD_CONFIG_DIRECTORY` | `~/.config` | Directory holding the config and session files. |

## 💡 Features

* **Upload** and **download** multiple files (up to 4 GiB per file for premium users).
* **Interactive** mode.
* **Topics**: upload/download in forum topics, auto-create topics from folder names.
* **Albums** of up to 10 photos/videos, each captioned with its filename.
* **Skip** already-uploaded files; **resume** interrupted uploads; network retries.
* Add video **thumbs** (or custom thumbnails).
* **Split** and **join** large files.
* **Delete** local or remote file on success.
* Use **variables** in the **caption** message.
* Proxy support and parallel-connection speed boost.

## 🐋 Docker

Run telegram-upload without installing it on your system using Docker. Instead of `telegram-upload` and `telegram-download` you should use `upload` and `download`. Usage:

```console
$ docker run -v <files_dir>:/files/
             -v <config_dir>:/config
             -it nekmo/telegram-upload:master
             <command> <args>
```

* `<files_dir>`: upload or download directory.
* `<config_dir>`: Directory that will be created to store the telegram-upload configuration. It is created automatically.
* `<command>`: `upload` and `download`.
* `<args>`: `telegram-upload` and `telegram-download` arguments.

For example:

```console
$ docker run -v /media/data/:/files/
             -v $PWD/config:/config
             -it nekmo/telegram-upload:master
             upload file_to_upload.txt
```

## ❤️ Thanks

This project developed by [Nekmo](https://github.com/Nekmo) & [collaborators](https://github.com/Nekmo/telegram-upload/graphs/contributors) would not be possible without [Telethon](https://github.com/LonamiWebs/Telethon), the library used as a Telegram client.

Telegram-upload is licensed under the [MIT license](https://github.com/Nekmo/telegram-upload/blob/master/LICENSE).
