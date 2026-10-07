# Upload benchmarks

Upload speed depends on Telegram server load, your network, hardware, and machine load — so benchmark on your own
connection instead of trusting old numbers. (Historical result tables and graphs were removed from the repo because
they predated the current parallelism defaults.)

## What to tune

* `TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS` (default `8`): file chunks uploaded in parallel. More chunks can raise
  throughput and CPU use, but also increases 429/rate-limit errors.
* `TELEGRAM_UPLOAD_MAX_CONNECTIONS` (default `1`): parallel TCP connections. Raising it can trigger Flood Wait.

Telegram picks the part size from the file size (larger files use larger parts, up to 512 KiB). Start at the
defaults and change one variable at a time.

```console
$ TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS=4 telegram-upload video.mkv
```

## Run your own benchmark

The `upload_benchmark.py` script in `docs/` uploads a file with your account and times it:

```console
$ python3 ./upload_benchmark.py benchmark
```

Results land in `upload_benchmark.json` (git-ignored working data, not committed). Plot them and regenerate the
Markdown tables with:

```console
$ python3 ./upload_benchmark.py graphs
$ python3 ./upload_benchmark.py md
```

See [Troubleshooting](troubleshooting.md) for rate-limit guidance and [Configuration](configuration.md) for the
retry-related variables.
