# Installation

## Install this checkout

The checkout includes additional forum-topic options such as `--topic-depth` and `--dry-run`. From the repository root, install it with:

```console
$ uv tool install --python 3.11 --force .
```

Python 3.11 is currently recommended because this version of the project imports `distutils`, which was removed in Python 3.12.

Check the installed CLI options with:

```console
$ telegram-upload --help
```

## Install the stable PyPI release

```console
$ uv tool install --python 3.11 telegram-upload
```

The PyPI release may not contain the checkout-specific folder-topic, `--topic-depth`, or `--dry-run` changes. Use the local checkout if you need those features.

## Install from GitHub

To install the upstream master branch:

```console
$ uv tool install --python 3.11 https://github.com/Nekmo/telegram-upload/archive/refs/heads/master.zip
```

## Docker

Run without a local installation by mounting the files directory and configuration directory. Inside the container, use `upload` and `download`:

```console
$ docker run --rm \
    -v /media/data:/files \
    -v "$PWD/config:/config" \
    -it nekmo/telegram-upload:master \
    upload file_to_upload.txt
```

For a folder-tree topic upload, the corresponding mounted path might look like:

```console
$ docker run --rm \
    -v /media/data:/files \
    -v "$PWD/config:/config" \
    -it nekmo/telegram-upload:master \
    upload --to my_group -t /files/course --topic-depth 1 --dry-run
```

Confirm the Docker image contains the required options with `upload --help`; an image built from an older release may not include checkout-specific features.

## Next steps

* [Usage](usage.md) — full CLI workflows after installing.
* [Troubleshooting](troubleshooting.md) — fix install, authentication, and upload problems.
