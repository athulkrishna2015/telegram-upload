import json
import os
import tempfile
import unittest

from telegram_upload.upload_log import UploadLog


class TestUploadLog(unittest.TestCase):
    def test_records_and_matches_destination_topic_and_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'uploaded.json')
            log = UploadLog(path)
            log.record(-100123, 42, 'video.mp4', 1234)

            self.assertTrue(log.contains(-100123, 42, 'video.mp4', 1234))
            self.assertFalse(log.contains(-100123, 43, 'video.mp4', 1234))
            self.assertFalse(log.contains(-100124, 42, 'video.mp4', 1234))
            self.assertFalse(log.contains(-100123, 42, 'video.mp4', 1235))

            reloaded = UploadLog(path)
            self.assertTrue(reloaded.contains(-100123, 42, 'video.mp4', 1234))
            with open(path, encoding='utf-8') as stream:
                self.assertEqual(len(json.load(stream)['uploads']), 1)

    def test_name_is_written_without_absolute_local_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'uploaded.json')
            UploadLog(path).record('chat', None, 'lesson.mp4', 11)
            with open(path, encoding='utf-8') as stream:
                content = stream.read()
            self.assertIn('lesson.mp4', content)
            self.assertNotIn(directory, content)
