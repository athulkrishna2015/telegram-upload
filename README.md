![logo](https://raw.githubusercontent.com/Nekmo/telegram-upload/master/assets/logo.png)

[![pip-rating badge](https://raw.githubusercontent.com/Nekmo/telegram-upload/pip-rating-badge/pip-rating-badge.svg)](https://github.com/Nekmo/telegram-upload/actions/workflows/pip-rating.yml)
[![Latest Tests CI build status](https://img.shields.io/github/actions/workflow/status/Nekmo/telegram-upload/test.yml?style=flat-square&maxAge=2592000&branch=master)](https://github.com/Nekmo/telegram-upload/actions?query=workflow%3ATests)
[![Latest PyPI version](https://img.shields.io/pypi/v/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Python versions](https://img.shields.io/pypi/pyversions/telegram-upload.svg?style=flat-square)](https://pypi.org/project/telegram-upload/)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/Nekmo/telegram-upload.svg?style=flat-square)](https://codeclimate.com/github/Nekmo/telegram-upload)
[![Test coverage](https://img.shields.io/codecov/c/github/Nekmo/telegram-upload/master.svg?style=flat-square)](https://codecov.io/github/Nekmo/telegram-upload)
[![Github stars](https://img.shields.io/github/stars/Nekmo/telegram-upload?style=flat-square)](https://github.com/Nekmo/telegram-upload)

# telegram-upload

Telegram-upload uses your **personal Telegram account** to **upload** and **download** files up to **4 GiB** (2 GiB for free users). Turn Telegram into your personal ☁ cloud!

To install **this checkout**, including its topic-folder, `--topic-depth`, and `--dry-run` options, run this command from the repository root:

```console
$ uv tool install --python 3.11 --force .
```

Python 3.11 is used because the current code imports `distutils`, which was removed in Python 3.12.

To install the upstream PyPI release instead:

```console
$ uv tool install --python 3.11 telegram-upload
```

> The PyPI release may not include the checkout-specific topic-folder, `--topic-depth`, or `--dry-run` features documented here. Check `telegram-upload --help` for the installed command's options.

You can also install the upstream master branch from GitHub:

```console
$ uv tool install --python 3.11 https://github.com/Nekmo/telegram-upload/archive/refs/heads/master.zip
```

More installation options, including [Docker](#-docker), are available in the [📕 documentation](https://docs.nekmo.org/telegram-upload/installation.html).

![demo](https://raw.githubusercontent.com/Nekmo/telegram-upload/master/assets/telegram-upload-demo.gif)

## ❓ Quick start

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

### Preview and upload a folder tree to forum topics

Install this checkout to use `--dry-run` and `--topic-depth`. For example, preview a directory where each first-level folder becomes a topic, root files go to General, and deeper folders become pinned headings:

```console
$ telegram-upload --to my_group -t "/path/to/course" --topic-depth 1 --sort --skip --dry-run
```

When the preview looks right, run the same command without `--dry-run`:

```console
$ telegram-upload --to my_group -t "/path/to/course" --topic-depth 1 --sort --skip
```

Use `--topic-depth 2` to turn the next folder level into nested topics. See the [complete usage guide](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/usage.md) and [architecture notes](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/architecture.md) for routing details, dry-run behavior, skip matching, and resume semantics.

### Interactive mode

The **interactive option** (`--interactive`) allows you to choose the dialog and the files to download or upload with a **terminal 🪄 wizard**. It even **supports mouse**!

```console
$ telegram-upload --interactive    # Interactive upload
$ telegram-download --interactive  # Interactive download
```

[More info in the documentation](https://docs.nekmo.org/telegram-upload/usage.html#interactive-mode)

## Documentation and development

See the [documentation index](https://github.com/athulkrishna2015/telegram-upload/tree/master/docs) for installation, complete usage, architecture, and troubleshooting guides. Contributor setup and test instructions are in the [contributing guide](https://github.com/athulkrishna2015/telegram-upload/blob/master/docs/contributing.md).

Run unit tests locally:

```console
$ uv run --isolated --python 3.11 --with-requirements requirements-dev.txt python -m unittest discover
```

You can also run functional tests using the provided script (requires a `.env` file or local configuration):

```console
$ ./tests/functional_test.sh
```

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
