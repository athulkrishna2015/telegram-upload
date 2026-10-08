#!/usr/bin/env python3
"""Build a fresh local upload log from Telegram history.

Reads existing media messages and pinned folder headings from a forum
group and writes them to `.telegram-upload-log.json`, so a later
`telegram-upload --skip --upload-log[-file]` run can skip them without
scanning Telegram history. Nothing is uploaded, and no Telegram messages
are created, modified, or deleted.

Example:
    python tools/build_upload_log.py --to -1001234567890 \\
        -t /data/course --topic-depth 1
    python tools/build_upload_log.py --to my_group -t /data/course \\
        --topic-depth 2 --upload-log-file /tmp/course-log.json
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_upload.client import TelegramManagerClient  # noqa: E402
from telegram_upload.config import default_config  # noqa: E402
from telegram_upload.upload_files import UPLOAD_LOG_FILENAME  # noqa: E402
from telegram_upload.upload_log import UploadLog  # noqa: E402
from telegram_upload.utils import async_to_sync  # noqa: E402


def collect_topic_dirs(source, depth):
    """Return [(relative name parts, abs path)] for folders at depth 1..N."""
    found = []

    def walk(base, rel):
        try:
            children = sorted(os.scandir(base), key=lambda entry: entry.name)
        except OSError:
            return
        for child in children:
            if not child.is_dir():
                continue
            child_rel = rel + (child.name,)
            if len(child_rel) <= depth:
                found.append((child_rel, child.path))
                walk(child.path, child_rel)

    walk(source, ())
    return found


def topic_title(rel):
    return rel[0] if len(rel) == 1 else ' / '.join(rel)


def in_forum_topic(message):
    header = getattr(message, 'reply_to', None)
    return bool(header is not None and getattr(header, 'forum_topic', False))


def seed_from_history(client, entity, topic_id, log, general_only=False):
    """Record current media files and folder headings for one destination."""
    added = 0
    for message in client.iter_messages(entity, reply_to=topic_id):
        if general_only and in_forum_topic(message):
            continue
        text = message.text or ''
        if text.startswith('📂 **') and text.endswith('**') and len(text) > 8:
            name = text[4:-2]
            if not log.contains(entity, topic_id, f'📂 {name}', 0):
                added += 1
            log.record(entity, topic_id, f'📂 {name}', 0)
            continue
        remote_file = getattr(message, 'file', None)
        name = getattr(remote_file, 'name', None) if remote_file else None
        size = getattr(remote_file, 'size', None) if remote_file else None
        if not name or size is None:
            continue
        if not log.contains(entity, topic_id, name, size):
            added += 1
        log.record(entity, topic_id, name, size)
    return added


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--to', required=True, help='Destination group/chat entity.')
    parser.add_argument('-t', '--topic', required=True,
                        help='Local source folder whose layout defines the topics.')
    parser.add_argument('--topic-depth', type=int, default=1,
                        help='Folder levels that become topics (default 1).')
    parser.add_argument('--upload-log-file', default=None,
                        help='Write the fresh log here instead of <source>/.telegram-upload-log.json.')
    args = parser.parse_args(argv)

    source = os.path.abspath(args.topic)
    if not os.path.isdir(source):
        parser.error('-t/--topic must be a local source folder for this script.')
    if args.topic_depth < 1:
        parser.error('--topic-depth must be >= 1.')

    log_path = (os.path.abspath(args.upload_log_file) if args.upload_log_file
                else os.path.join(source, UPLOAD_LOG_FILENAME))
    if os.path.exists(log_path):
        print(f'Replacing existing log: {log_path}')
        os.remove(log_path)
    log = UploadLog(log_path)

    entity = args.to
    if isinstance(entity, str) and entity.lstrip('-+').isdigit():
        entity = int(entity)
    client = TelegramManagerClient(default_config())
    client.start()

    total = 0
    destinations = [(None, 'General')]
    for rel, _path in collect_topic_dirs(source, args.topic_depth):
        title = topic_title(rel)
        topic_id = async_to_sync(client.find_topic(entity, title))
        if topic_id is None:
            print(f'No existing topic {title!r}; nothing to seed for it.')
            continue
        destinations.append((topic_id, title))

    for topic_id, label in destinations:
        added = seed_from_history(client, entity, topic_id, log,
                                  general_only=topic_id is None)
        total += added
        print(f'{label}: seeded {added} records.')

    print(f'Wrote {len(log.entries)} entries to {log_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
