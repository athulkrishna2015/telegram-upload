
.. image:: https://raw.githubusercontent.com/Nekmo/telegram-upload/master/logo.png
    :width: 100%

|

.. image:: https://raw.githubusercontent.com/Nekmo/telegram-upload/pip-rating-badge/pip-rating-badge.svg
  :target: https://github.com/Nekmo/telegram-upload/actions/workflows/pip-rating.yml
  :alt: pip-rating badge

.. image:: https://img.shields.io/github/actions/workflow/status/Nekmo/telegram-upload/test.yml?style=flat-square&maxAge=2592000&branch=master
  :target: https://github.com/Nekmo/telegram-upload/actions?query=workflow%3ATests
  :alt: Latest Tests CI build status

.. image:: https://img.shields.io/pypi/v/telegram-upload.svg?style=flat-square
  :target: https://pypi.org/project/telegram-upload/
  :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/pyversions/telegram-upload.svg?style=flat-square
  :target: https://pypi.org/project/telegram-upload/
  :alt: Python versions

.. image:: https://img.shields.io/codeclimate/maintainability/Nekmo/telegram-upload.svg?style=flat-square
  :target: https://codeclimate.com/github/Nekmo/telegram-upload
  :alt: Code Climate

.. image:: https://img.shields.io/codecov/c/github/Nekmo/telegram-upload/master.svg?style=flat-square
  :target: https://codecov.io/github/Nekmo/telegram-upload
  :alt: Test coverage

.. image:: https://img.shields.io/github/stars/Nekmo/telegram-upload?style=flat-square
     :target: https://github.com/Nekmo/telegram-upload
     :alt: Github stars


###############
telegram-upload
###############
Telegram-upload uses your **personal Telegram account** to **upload** and **download** files up to **4 GiB** (2 GiB for
free users). Turn Telegram into your personal ☁ cloud!

To **install 🔧 telegram-upload**, run this command in your terminal:

.. code-block:: console

    $ uv tool install telegram-upload

Or install the most recent stable release from GitHub:

.. code-block:: console

    $ uv tool install https://github.com/Nekmo/telegram-upload/archive/refs/heads/master.zip

Alternatively, you can use pip:

.. code-block:: console

    $ sudo pip3 install telegram-upload
🐍 **Python 3.7-3.14** are tested and supported. There are other installation ways available like `Docker <#-docker>`_.
More info in the `📕 documentation <https://docs.nekmo.org/telegram-upload/installation.html>`_

.. image:: https://raw.githubusercontent.com/Nekmo/telegram-upload/master/telegram-upload-demo.gif
  :target: https://asciinema.org/a/592098
  :width: 100%

❓ Usage
========
To use this program you need an Telegram account and your **App api_id & api_hash** (get it in
`my.telegram.org <https://my.telegram.org/>`_). The first time you use telegram-upload it requests your
📱 **telephone**, **api_id** and **api_hash**. Bot tokens can not be used with this program (bot uploads are limited to
50MB).

To **send ⬆️ files** (by default it is uploaded to saved messages):

.. code-block:: console

    $ telegram-upload file1.mp4 file2.mkv

You can **download ⤵️ the files** again from your saved messages (by default) or from a channel. All files will be
downloaded until the last text message.

.. code-block:: console

    $ telegram-download

`Read the documentation <https://docs.nekmo.org/telegram-upload/usage.html#telegram-download>`_ for more info about the
options availables.

Interactive mode
----------------
The **interactive option** (``--interactive``) allows you to choose the dialog and the files to download or upload with
a **terminal 🪄 wizard**. It even **supports mouse**!

.. code-block:: console

    $ telegram-upload --interactive    # Interactive upload
    $ telegram-download --interactive  # Interactive download

`More info in the documentation <https://docs.nekmo.org/telegram-upload/usage.html#interactive-mode>`_

Set group or chat
-----------------
By default when using telegram-upload without specifying the recipient or sender, telegram-upload will use your personal
chat. However you can define the 👨 destination. For file upload the argument is ``--to <entity>``. For example:

.. code-block::

    $ telegram-upload --to telegram.me/joinchat/AAAAAEkk2WdoDrB4-Q8-gg video.mkv

You can also upload or download files from a specific **topic** in a forum-enabled group using the ``--topic <id_or_name>`` (or ``-t <id_or_name>``) parameter:

.. code-block::

    $ telegram-upload --to my_group --topic 42 video.mkv
    $ telegram-upload --to my_group --topic "Physics Class" video.mkv

If you provide a **directory path** to the topic flag, the tool will automatically create a topic with the folder's name (if it doesn't exist) and upload all files inside that folder to that topic.

However, if you pass a folder as a **positional argument** (without ``-t``), it will upload all files inside it to the main chat or the "General" topic. By default folders are processed recursively, but you can also use the ``--recursive`` (or ``-r``) flag explicitly:

.. code-block:: console

    # Upload files in folder to the main chat (no topic created)
    $ telegram-upload --to my_group "/path/to/Nuclear Physics"
    $ telegram-upload --to my_group -r "/path/to/Nuclear Physics"

    # Automatically create/find topic "Nuclear Physics" and upload its content there
    $ telegram-upload --to my_group -t "/path/to/Nuclear Physics"

Telegram-upload supports **multiple destinations** in a single command. You can **distribute** different files to different topics using the ``--distribute`` flag. This will divide the files among the destinations:

.. code-block:: console

    # Send file1.zip to Topic 1 and file2.zip to Topic 2
    $ telegram-upload --to my_group -t 1 -t 2 --distribute file1.zip file2.zip

For **explicit mapping**, you can repeat the topic flag followed by the specific files for that topic (1-to-1 mapping). Comma-separated lists are also supported. You can even use multiple groups as "buckets" for sets of topics:

.. code-block:: console

    # Send file1 to Topic 1 and file2 to Topic 2
    $ telegram-upload --to MyGroup -t 1 "file1.zip" -t 2 "file2.zip"

    # Multiple folders to different topics
    $ telegram-upload --to MyGroup -t "./Folder1" -t "./Folder2"

    # Advanced: 2 files to Topic 1 & 2 in Group A, and 2 files to Topic 1 & 2 in Group B
    $ telegram-upload --to GroupA -t 1 "file1" -t 2 "file2" --to GroupB -t 1 "file3" -t 2 "file4"

    # Multiple files per topic using commas
    $ telegram-upload --to MyGroup -t 442 "vid1.mp4,pdf1.pdf" -t 445 "vid2.mp4"

You can see all `the possible values for the entity in the documentation <https://docs.nekmo.org/telegram-upload/usage.html#set-recipient-or-sender>`_.

Performance & Speed
-------------------
To **improve upload speed**, you can increase the number of parallel upload blocks and use multiple connections (Speed Boost).

*   ``TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS``: Number of chunks sent in parallel. Default is ``8``.
*   ``TELEGRAM_UPLOAD_MAX_CONNECTIONS``: Number of parallel TCP connections to use. Default is ``1``. Increasing this can significantly boost speed for high-bandwidth connections.

.. code-block:: console

    # Boost speed using 16 parallel blocks and 4 connections
    $ export TELEGRAM_UPLOAD_PARALLEL_UPLOAD_BLOCKS=16
    $ export TELEGRAM_UPLOAD_MAX_CONNECTIONS=4
    $ telegram-upload large-file.zip

Note: Using too many connections may lead to temporary rate limits (Flood Wait) from Telegram.

Split & join files
------------------
If you try to upload a file that **exceeds the maximum supported** by Telegram by default, an error will occur. But you
can enable ✂ **split mode** to upload multiple files:

.. code-block:: console

    $ telegram-upload --large-files split large-video.mkv

Files split using split can be rejoined on download using:

.. code-block:: console

    $ telegram-download --split-files join

Find more help in `the telegram-upload documentation <https://docs.nekmo.org/telegram-upload/usage.html#split-files>`_.

Delete on success
-----------------
The ``--delete-on-success`` option allows you to ❌ **delete the Telegram message** after downloading the file. This is
useful to send files to download to your saved messages and avoid downloading them again. You can use this option to
download files on your computer away from home.

Configuration
-------------
Credentials are saved in ``~/.config/telegram-upload.json`` and ``~/.config/telegram-upload.session``. You must make
sure that these files are secured. You can copy these 📁 files to authenticate ``telegram-upload`` on more machines, but
it is advisable to create a session file for each machine.

More options
------------
Telegram-upload has more options available, like customizing the files thumbnail, set a caption message (including
variables) or configuring a proxy.
`Read the documentation <https://docs.nekmo.org/telegram-upload/usage.html#telegram-download>`_ for more info.

💡 Features
===========

* **Upload** and **download** multiples files  (up to 4 GiB per file for premium users).
* **Interactive** mode.
* Add video **thumbs**.
* **Split** and **join** large files.
* **Delete** local or remote file on success.
* Use **variables** in the **caption** message.
* ... And **more**.

🐋 Docker
=========
Run telegram-upload without installing it on your system using Docker. Instead of ``telegram-upload``
and ``telegram-download`` you should use ``upload`` and ``download``. Usage::


    $ docker run -v <files_dir>:/files/
                 -v <config_dir>:/config
                 -it nekmo/telegram-upload:master
                 <command> <args>

* ``<files_dir>``: upload or download directory.
* ``<config_dir>``: Directory that will be created to store the telegram-upload configuration.
  It is created automatically.
* ``<command>``: ``upload`` and ``download``.
* ``<args>``: ``telegram-upload`` and ``telegram-download`` arguments.

For example::

    $ docker run -v /media/data/:/files/
                 -v $PWD/config:/config
                 -it nekmo/telegram-upload:master
                 upload file_to_upload.txt

❤️ Thanks
=========
This project developed by `Nekmo <https://github.com/Nekmo>`_ & `collaborators <https://github.com/Nekmo/telegram-upload/graphs/contributors>`_ would not be possible without
`Telethon <https://github.com/LonamiWebs/Telethon>`_, the library used as a Telegram client.

Telegram-upload is licensed under the `MIT license <https://github.com/Nekmo/telegram-upload/blob/master/LICENSE>`_.
