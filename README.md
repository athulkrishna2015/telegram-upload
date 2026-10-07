![logo](https://raw.githubusercontent.com/athulkrishna2015/telegram-upload/master/assets/logo.png)

[![pip-rating badge](https://raw.githubusercontent.com/Nekmo/telegram-upload/pip-rating-badge/pip-rating-badge.svg)](https://github.com/Nekmo/telegram-upload/actions/workflows/pip-rating.yml)
[![Latest Tests CI build status](https://img.shields.io/github/actions/workflow/status/Nekmo/telegram-upload/test.yml?style=flat-square&maxAge=2592000&branch=master)](https://github.com/Nekmo/telegram-upload/actions?query=workflow%3ATests)
[![Latest PyPI version](https://img.shields.io/pypi/v/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Python versions](https://img.shields.io/pypi/pyversions/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/Nekmo/telegram-upload.svg?style=flat-square)](https://codeclimate.com/github/Nekmo/telegram-upload)
[![Test coverage](https://img.shields.io/codecov/c/github/Nekmo/telegram-upload/master.svg?style=flat-square)](https://codecov.io/github/Nekmo/telegram-upload)
[![Github stars](https://img.shields.io/github/stars/Nekmo/telegram-upload?style=flat-square)](https://github.com/Nekmo/telegram-upload)

# telegram-upload

Use your **personal Telegram account** to **upload** and **download** files through chats, channels, and forum
topics — up to **2 GiB** per file (4 GiB for Premium users). Videos and images are sent as streamable media, not
plain documents.

![demo](https://raw.githubusercontent.com/athulkrishna2015/telegram-upload/master/assets/telegram-upload-demo.gif)

## Install

Install this checkout (includes folder-topic uploads, `--topic-depth`, and `--dry-run`):

```console
$ uv tool install --python 3.11 --force .
```

Python 3.11 is used because the current code imports `distutils`, which was removed in Python 3.12.

```console
$ telegram-upload --help
```

> The PyPI release may not include the checkout-specific topic-folder, `--topic-depth`, or `--dry-run` features
> documented here. Check `telegram-upload --help` for the installed command's options.

See the [installation guide](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/installation.md)
for PyPI, GitHub, and Docker installs.

## Quick start

You need a Telegram account and your **App api_id & api_hash** (get them in [my.telegram.org](https://my.telegram.org/)).
The first run requests your 📱 **telephone**, **api_id** and **api_hash** interactively. Bot tokens can not be used
with this program (bot uploads are limited to 50MB).

```console
$ telegram-upload file1.mp4 file2.mkv        # to Saved Messages
$ telegram-upload --to my_group video.mkv    # to a group
$ telegram-download                          # fetch them back
```

Preview a folder-to-topics upload before sending anything (root files go to General, first-level folders become
topics, deeper folders become pinned headings):

```console
$ telegram-upload --to my_group -t "/path/to/course" --topic-depth 1 --sort --skip --dry-run
```

Remove `--dry-run` to run it for real. Use `--topic-depth 2` for nested topics, `--interactive` for a terminal
wizard, and rerun the same command to resume interrupted files or `--skip` completed ones.

## Guides

* [Quick start](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/quickstart.md) — first run, destinations, interactive mode.
* [Usage reference](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/usage.md) — every flag for both commands.
* [Folder trees to forum topics](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/topics.md) — `--topic-depth` layouts and dry-run output.
* [Configuration](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/configuration.md) — config files, proxies, environment variables.
* [Architecture](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/architecture.md) — planning, upload pipeline, and state map.
* [Troubleshooting](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/troubleshooting.md) — common failures and fixes.
* [Caption format](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/caption_format.md) — caption variables for uploaded files.
* [Supported file types](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/supported_file_types.md) — media feature matrix.
* [Upload benchmarks](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/upload_benchmark.md) — parallelism measurements.
* [Contributing](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/contributing.md) — development setup and running tests.

## Notes

* `--skip` matches by filename/size per destination; interrupted files resume from local progress state.
* Never share `~/.config/telegram-upload.json`, `*.session` files, or your `api_hash`.

Run unit tests locally:

```console
$ uv run --isolated --python 3.11 --with-requirements requirements-dev.txt python -m unittest discover
```

Functional tests need a local Telegram configuration:

```console
$ ./tests/functional_test.sh
```

## 🐋 Docker

Run telegram-upload without installing it on your system using Docker. Instead of `telegram-upload` and
`telegram-download` you should use `upload` and `download`. Usage:

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

Based on [Nekmo/telegram-upload](https://github.com/Nekmo/telegram-upload), built on
[Telethon](https://github.com/LonamiWebs/Telethon). Licensed under the
[MIT license](https://github.com/athulkrishna2015/telegram-upload/blob/master/LICENSE).
