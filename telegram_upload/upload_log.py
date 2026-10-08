"""Persistent local cache for completed upload identities."""

import json
import os
import threading


class UploadLog:
    """A small JSON upload cache, scoped to Telegram destination and topic.

    The log intentionally stores only destination/topic IDs, basename, and
    size. It does not store local absolute paths or file contents.
    """

    def __init__(self, path):
        self.path = os.path.abspath(os.path.expanduser(path))
        self._lock = threading.Lock()
        try:
            with open(self.path, 'r', encoding='utf-8') as stream:
                data = json.load(stream)
        except (OSError, ValueError):
            data = {}
        self.entries = set(data.get('uploads', []))

    @staticmethod
    def key(entity, topic, name, size):
        return json.dumps([str(entity), str(topic or ''), name, int(size)], ensure_ascii=False)

    def contains(self, entity, topic, name, size):
        return self.key(entity, topic, name, size) in self.entries

    def record(self, entity, topic, name, size):
        entry = self.key(entity, topic, name, size)
        with self._lock:
            if entry in self.entries:
                return
            self.entries.add(entry)
            self._save()

    def _save(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        temporary = self.path + '.tmp'
        with open(temporary, 'w', encoding='utf-8') as stream:
            json.dump({'version': 1, 'uploads': sorted(self.entries)}, stream,
                      ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, self.path)
