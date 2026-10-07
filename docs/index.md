# Welcome to telegram-upload's documentation!

Telegram-upload uses your personal Telegram account to upload and download files up to 4 GiB (2 GiB for free users).
Turn Telegram into your personal cloud!


To install the latest stable release, use `uv`:

```console
$ uv tool install --python 3.11 telegram-upload
```

For the checkout-specific topic-folder, `--topic-depth`, and `--dry-run` options documented here, install the project checkout with `uv tool install --python 3.11 --force .` from the repository root. See [Installation](installation.md).

## Guides

* [Installation](installation.md) — install this checkout, the PyPI release, or Docker.
* [Usage](usage.md) — CLI workflows, folder-topic mapping, dry-run, skip, and resume.
* [Architecture](architecture.md) — planning, upload pipeline, and state map.
* [Troubleshooting](troubleshooting.md) — diagnose install, topic, upload, and performance issues.
* [Caption format](caption_format.md) — caption variables for uploaded files.
* [Supported file types](supported_file_types.md) — media feature matrix.
* [Upload benchmarks](upload_benchmark.md) — parallelism measurements.
* [Contributing](contributing.md) — development and test workflow.

## Contents


```{toctree}
:maxdepth: 2
:glob:

installation
readme
usage
architecture
troubleshooting
caption_format
supported_file_types
upload_benchmark
contributing
authors
history
```
