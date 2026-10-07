
# Usage


```{eval-rst}
.. click:: telegram_upload.management:upload
   :prog: telegram-upload
   :show-nested:


```

```{eval-rst}
.. click:: telegram_upload.management:download
   :prog: telegram-download
   :show-nested:

```

## Set recipient or sender

By default when using *telegram-upload* without specifying the recipient or sender, *telegram-upload* will use your
personal chat. This is especially useful because you can use it to upload files from telegram-upload and then forward
them from your personal chat to as many groups as you like. However you can define the destination. For file upload the
argument is `--to <entity>`:

```
~ $ telegram-upload --to <entity> <file 1>[ <file 2>]
```

You can *download files* from a specific chat using the `--from <entity>` parameter:

```
~ $ telegram-download --from <entity>
```

The entity can be defined in multiple ways:

* **Username or groupname**: use the public username or groupname. For example: *john*.
* **Public link**: the public user or group link. For example: *https://telegram.dog/john*.
* **Private link**: the private group link. For example: *telegram.me/joinchat/AAAAAEkk2WdoDrB4-Q8-gg*.
* **Telephone**: the user telephone. For example: *+34600000000*.
* **Telegram id**: the user or group telegram id. Use a bot like *@getidsbot* for get the id. For example: *-987654321*
  or *123456789*.

## Forum topics and folder trees

Use `--topic` (`-t`) to send files to a forum topic by its numeric ID or title. If the topic title does not exist, a normal upload creates it. The group must have forum topics enabled and the account must have permission to create topics.

```console
$ telegram-upload --to my_group --topic 42 video.mkv
$ telegram-upload --to my_group --topic "Physics Class" video.mkv
```

Passing a directory as the topic value uses that directory's basename as the topic name and uploads its contents recursively into that topic:

```console
$ telegram-upload --to my_group -t "/data/Physics Class"
```

### Use folder levels as topics

Use `--topic-depth N` to map a source directory's hierarchy to forum topics. The `-t` directory is the source root:

* Files directly inside the source root are sent to General.
* Each non-empty folder up to level `N` becomes a topic.
* Level-1 topics use the child folder name. Nested topics use relative names such as `CHEMISTRY / INTRODUCTION` to distinguish identical folder names under different parents.
* Folders below level `N` remain in their nearest topic. Each deeper directory is announced and pinned as a `📂` message; its files remain in that topic.
* Empty folders do not create topics.
* Existing matching topics are reused, and missing topics are created during real upload. A dry run only looks up topics and does not create them.

`N` must be an integer greater than or equal to 1. Without `--topic-depth`, a `-t` directory continues to mean one topic named after the source directory. For example:

```text
Xylem_LPUP/
├── root-index.txt
└── CHEMISTRY/
    ├── overview.mp4
    └── INTRODUCTION/
        └── lesson.mp4
```

At depth 1, `root-index.txt` goes to General, both videos go to topic `CHEMISTRY`, and `INTRODUCTION` is a pinned folder announcement in that topic. At depth 2, `INTRODUCTION` becomes a topic titled `CHEMISTRY / INTRODUCTION`.

The same rule applies at each folder level. For a tree `Root/A/B/C/file.txt`, `--topic-depth 1` creates topic `A` and pins `B` and `C` there; depth 2 creates `A` and `A / B` and pins `C` in the latter; depth 3 creates `A`, `A / B`, and `A / B / C`. Files in `Root/` always go to General.

```console
# Preview destinations, topic creation, uploads, skips, and folder announcements
$ telegram-upload --to my_group -t "/data/Xylem_LPUP" --topic-depth 1 --sort --skip --dry-run

# Run the upload; --skip is useful if you need to rerun after completed files
$ telegram-upload --to my_group -t "/data/Xylem_LPUP" --topic-depth 1 --sort --skip
```

### Dry run

`--dry-run` prints a per-destination summary and the planned file actions. It does not send messages, upload file parts, pin folder announcements, create topics, or delete local files. Telegram access is still used to resolve the destination and look up topic names; with `--skip`, it reads destination history to identify files that would be skipped. For a topic that does not exist yet, the dry run reports that it *would create* the topic and lists its files as uploads because there is no history to compare.

Example output:

```text
[dry-run] to my_group General: 1 to upload (1024 bytes), 0 skipped, 0 announcements
[dry-run] to my_group topic "CHEMISTRY" (would create): 2 to upload (12345 bytes), 0 skipped, 1 announcements
[dry-run]   upload /data/Xylem_LPUP/CHEMISTRY/lesson.mp4 (12000 bytes)
[dry-run]   announce+pin 📂 INTRODUCTION
```

Dry run is a planning aid, not a guarantee that Telegram will accept every file or topic operation when the real upload runs.

For implementation details on planning, skip matching, progress state, and module responsibilities, see [Architecture](architecture.md).

## Interactive mode

Use the `-i` (or `--interactive`) option to activate the **interactive mode** to choose the dialog (chat,
channel...) and the files. To **upload files** using interactive mode:

    $ telegram-upload -i

To **download files** using interactive mode:

    $ telegram-download -i

The following keys are available in this mode:

* **Up arrow**: previous option in the list.
* **Down arrow**: next option in the list.
* **Spacebar**: select the current option. The selected option is marked with an asterisk.
* **mouse click**: also to select the option. Some terminals may not support it.
* **Enter**: go to the next wizard step.
* **pageup**: go to the previous page of items. Allows quick navigation..
* **pagedown**: go to the next page of items. Allows quick navigation..

### Interactive upload

This wizard has two steps. The *first step* chooses the files to upload. You can choose several files:
```console
Select the local files to upload:
[SPACE] Select file [ENTER] Next step
[ ] myphoto1.jpg
[ ] myphoto2.jpg
[ ] myphoto3.jpg
```

The *second step* chooses the conversation:
```console
Select the dialog of the files to download:
[SPACE] Select dialog [ENTER] Next step
( ) Groupchat 1
( ) Bob's chat
( ) A channel
( ) Me
```

### Interactive download

This wizard has two steps. The *first step* chooses the conversation:
```console
Select the dialog of the files to download:
[SPACE] Select dialog [ENTER] Next step
( ) Groupchat 1
( ) Bob's chat
( ) A channel
( ) Me
```

The *second step* chooses the files to download. You can choose several files:
```console
Select all files to download:
[SPACE] Select files [ENTER] Download selected files
[ ] image myphoto3.jpg by My Username @username 2022-01-31 02:15:07+00:00
[ ] image myphoto2.jpg by My Username @username 2022-01-31 02:15:05+00:00
[ ] image myphoto1.png by My Username @username 2022-01-31 02:15:03+00:00
```

## Proxies

You can use **mtproto proxies** without additional dependencies or **socks4**, **socks5** or **http** proxies
installing `pysocks`. To install it:
```console
$ pip install pysocks
```

To define the proxy you can use the `--proxy` parameter:
```console
$ telegram-upload image.jpg --proxy mtproxy://secret@proxy.my.site:443
```

Or you can define one of these variables: `TELEGRAM_UPLOAD_PROXY`, `HTTPS_PROXY` or `HTTP_PROXY`. To define the
environment variable from terminal:
```console
$ export HTTPS_PROXY=socks5://user:pass@proxy.my.site:1080
$ telegram-upload image.jpg
```

Parameter `--proxy` has higher priority over environment variables. The environment variable
`TELEGRAM_UPLOAD_PROXY` takes precedence over `HTTPS_PROXY` and it takes precedence over `HTTP_PROXY`. To disable
the OS proxy:
```console
$ export TELEGRAM_UPLOAD_PROXY=
$ telegram-upload image.jpg
```

The syntax for **mproto proxy** is:
```console
mtproxy://<secret>@<address>:<port>
```

For example:
```console
mtproxy://secret@proxy.my.site:443
```

The syntax for **socks4**, **socks5** and **http** proxy is:
```console
<protocol>://[<username>:<password>@]<address>:<port>
```

An example without credentials:
```console
http://1.2.3.4:80
```

An example with credentials:
```console
socks4://user:pass@proxy.my.site:1080
```

## Caption message

You can add a caption message to the file to upload using the `--caption` parameter:
```console
$ telegram-upload image.jpg --caption "This is a caption"
```

This parameter support variables using the `{}` syntax. For example:
```console
$ telegram-upload image.jpg --caption "This is a caption for {file.stem.capitalize}"
```

The `{file}` variable is the file path. The `{file.stem}` variable is the file name without extension. The
`{file.stem.capitalize}` variable is the file name without extension with the first letter in uppercase. The
`{file}` variable has attributes for get info about the file like their size, their creation date, their checksums
(md5, sha1, sha256...), their media info (width, height, artist...) and more. For example:
```console
$ telegram-upload image.jpg --caption "{file.media.width}x{file.media.height}px {file.media.duration.for_humans}"
```

If you want to use the `{}` syntax in the caption message, you can escape it using the brace twice. For example:
```console
$ telegram-upload image.jpg --caption "This is a caption with {{}}"
```

For get more info about the variables, see the [caption format](caption_format.md) section.

## Split files

By default, when trying to **upload** a file larger than the supported size by Telegram, an error will occur. However,
*Telegram-upload* has different policies for large files using the `--large-files` parameter:

* `fail` (default): The execution of telegram-upload is stopped and the uploads are not continued.
* `split`: The files are split as parts. For example *myfile.tar.00*, *myfile.tar.01*...

The syntax is:

```
~$ telegram-upload --large-files <fail|split>
```

To join the split files using the *split* option, you can use in GNU/Linux:

```bash
$ cat myfile.tar.* > myfile.tar
```

In windows there are different programs like [7z](https://7-zip.org/) or [GSplit](https://www.gdgsoft.com/gsplit).

*Telegram-upload* when downloading split files by default will download the files without joining them. However, the
**download** policy can be changed using the `--split-files` parameter:

* `keep` (default): Files are downloaded without joining.
* `join`: Downloaded files are merged after downloading. In case of errors, such as missing files, the keep policy
  is used.

The syntax is:

```
$ telegram-download --split-files <keep|join>
```

## Skip already uploaded

You can skip files that have already been uploaded to the destination chat using the `--skip` (or `-s`) flag.
This compares filename and size (photos may be matched by caption filename or stem); it does not compare content hashes. Keep the same destination and topic options for reruns. A changed file with the same filename and size may be considered a duplicate.

```
$ telegram-upload --skip video.mp4
```

## Resume support

Telegram-upload automatically resumes interrupted uploads for large files. If an upload is stopped, simply run the
same command again, and it will pick up from the last successfully uploaded part.

Progress is tracked in `~/.config/telegram-upload-progress.json`. It records uploaded parts for the currently interrupted file and is cleared when that file completes. Rerun the same command with the same file path and size to resume. Resume state does not suppress files that already completed; combine with `--skip` to skip completed files on reruns.

## Network Resilience

The tool is designed to be resilient to network drops. It will persistently retry connection errors and timeouts,
making it suitable for long-running uploads on unstable connections.
