import os
import unittest
from unittest.mock import MagicMock
import asyncio

from telethon.tl.types import DocumentAttributeFilename, User

from ._compat import patch

from click.testing import CliRunner

from telegram_upload.management import upload, download, get_file_display_name

directory = os.path.dirname(os.path.abspath(__file__))


class TestGetFileDisplayName(unittest.TestCase):
    def test_get_file_display_name(self):
        mock_message = MagicMock()
        mock_message.document.mime_type = "text/plain"
        mock_message.document.attributes = [DocumentAttributeFilename("test.txt")]
        mock_message.text = "text"
        mock_message.sender = User(
            1000, first_name="first_name", last_name="last_name", username="username",
        )
        mock_message.date = "date"
        display_name = get_file_display_name(mock_message)
        self.assertEqual('text test.txt [text] by first_name last_name @username date', display_name)


class TestUpload(unittest.TestCase):

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024
        test_file = os.path.join(directory, 'test_management.py')
        runner = CliRunner()
        result = runner.invoke(upload, [test_file])
        self.assertEqual(result.exit_code, 0)
        mock_client.assert_called_once()
        mock_client.return_value.send_files.assert_called_once()

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_multiple_files_single_topic(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024
        
        async def mock_get_topic(entity, title):
            return 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic
        
        test_file1 = os.path.join(directory, 'file1.txt')
        test_file2 = os.path.join(directory, 'file2.txt')
        runner = CliRunner()
        # This should NOT fail now
        result = runner.invoke(upload, ['--to', 'me', '--topic', 'MyTopic', test_file1, test_file2])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_client.return_value.send_files.assert_called_once()

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_interleaved_topics_files(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return int(title) if str(title).isdigit() else 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic

        test_file1 = os.path.join(directory, 'file1.txt')
        test_file2 = os.path.join(directory, 'file2.txt')

        # We need to simulate sys.argv for the interleaved logic
        import sys
        original_argv = sys.argv
        sys.argv = ['telegram-upload', '--to', 'me', '-t', '1', test_file1, '-t', '2', test_file2]

        try:
            runner = CliRunner()
            result = runner.invoke(upload, ['--to', 'me', '-t', '1', test_file1, '-t', '2', test_file2])
            self.assertEqual(result.exit_code, 0, result.output)
            # send_files should be called twice, once for each topic
            self.assertEqual(mock_client.return_value.send_files.call_count, 2)

            # Check arguments of calls
            # First call: topic 1
            args1 = mock_client.return_value.send_files.call_args_list[0]
            self.assertEqual(args1.kwargs['reply_to'], 1)
            # Second call: topic 2
            args2 = mock_client.return_value.send_files.call_args_list[1]
            self.assertEqual(args2.kwargs['reply_to'], 2)
        finally:
            sys.argv = original_argv

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_exclusive(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(upload, ['missing_file.txt', '--thumbnail-file', 'cara128.png', '--no-thumbnail'])
        self.assertEqual(result.exit_code, 2)
        m1.return_value.send_files.assert_not_called()


class TestDownload(unittest.TestCase):
    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_download(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(download, [])
        self.assertEqual(result.exit_code, 0)
        m1.assert_called_once()
        m1.return_value.download_files.assert_called_once()
