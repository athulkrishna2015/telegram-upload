# Configuration

## Files

| File | Purpose |
|---|---|
| `~/.config/telegram-upload.json` | `api_id`, `api_hash`, session reference. Created on first run. |
| `~/.config/telegram-upload.session` | Telethon login session. Only one process may hold it at a time. |
| `~/.config/telegram-upload-progress.json` | Per-file uploaded-part records for resume; entries are removed on completion. |

Local upload caching is opt-in. Use `--skip --upload-log` to create `.telegram-upload-log.json` in the source folder,
or `--skip --upload-log-file PATH` to select a cache location. The cache records successful
destination/topic/name/size tuples, is not seeded from Telegram, and does not detect remote deletions. The default
cache name is reserved and excluded from recursive uploads.

Protect all three. Never publish them or paste their contents into logs or tickets. Copying the JSON + session to
another machine transfers the login; prefer a dedicated session per machine. `--config` selects an alternate config
file. To run concurrent uploads, duplicate the session/config pair and pass `--config` per process.

## Proxies

`--proxy` accepts `mtproxy://<secret>@<host>:<port>` and `http|socks4|socks5://[user:pass@]host:port` (SOCKS/HTTP
needs the optional `pysocks` package). Without `--proxy`, the fallback chain is `TELEGRAM_UPLOAD_PROXY` →
`HTTPS_PROXY` → `HTTP_PROXY`; set `TELEGRAM_UPLOAD_PROXY=` (empty) to disable OS proxies.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS` | `8` | File chunks uploaded in parallel. Lower it if Telegram returns 429/rate-limit errors. |
| `TELEGRAM_UPLOAD_MAX_CONNECTIONS` | `1` | Parallel TCP connections (speed boost; raising it risks Flood Wait). |
| `TELEGRAM_UPLOAD_MAX_RECONNECT_RETRIES` | `5` | Reconnect attempts after network failures. |
| `TELEGRAM_UPLOAD_RECONNECT_TIMEOUT` | `5` | Max seconds to wait per reconnect attempt. |
| `TELEGRAM_UPLOAD_MIN_RECONNECT_WAIT` | `2` | Base wait before retrying a failed part (grows with retries). |
| `TELEGRAM_UPLOAD_PARALLEL_DOWNLOAD_BLOCKS` | `10` | Download chunks fetched in parallel. |
| `TELEGRAM_UPLOAD_SESSION` | — | Session-string override instead of the session file. |
| `TELEGRAM_UPLOAD_CONFIG_DIRECTORY` | `~/.config` | Directory holding the config and session files. |
