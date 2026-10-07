import os
import tempfile
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
        
        async def mock_check_topic(entity, topic_id):
            return True
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic
        
        test_file1 = os.path.join(directory, 'file1.txt')
        test_file2 = os.path.join(directory, 'file2.txt')
        runner = CliRunner()
        # This should NOT fail now
        result = runner.invoke(upload, ['--to', 'me', '--topic', 'MyTopic', test_file1, test_file2])
        self.assertEqual(result.exit_code, 0, result.output)
        mock_client.return_value.send_files.assert_called_once()

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_existing_path_with_comma(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_check_topic(entity, topic_id):
            return True

        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, 'file,with-comma.txt')
            with open(path, 'w') as file:
                file.write('test')
            result = CliRunner().invoke(upload, ['--to', 'me', '--topic', '5', path])

        self.assertEqual(result.exit_code, 0, result.output)
        files = mock_client.return_value.send_files.call_args[0][1]
        self.assertEqual(1, len(files))
        self.assertEqual(path, files[0].path)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_interleaved_topics_files(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return int(title) if str(title).isdigit() else 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic

        async def mock_check_topic(entity, topic_id):
            return True
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic

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
    def test_upload_topic_folder_recursive(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic
        
        async def mock_check_topic(entity, topic_id):
            return True
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic

        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            test_file = os.path.join(sub_dir, 'file.txt')
            with open(test_file, 'w') as f:
                f.write('content')

            runner = CliRunner()
            # Use the temp_dir as a topic
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir])
            self.assertEqual(result.exit_code, 0, result.output)
            
            # send_files should be called with the file from the subdir 
            # and a DirectoryMarker for the subdir
            mock_client.return_value.send_files.assert_called_once()
            args = mock_client.return_value.send_files.call_args
            files_sent = list(args[0][1])
            self.assertEqual(len(files_sent), 2)
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_recursive_with_subfolder_announcement(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic
        
        async def mock_check_topic(entity, topic_id):
            return True
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic

        # Mock sync methods because telethon.sync is used
        mock_client.return_value.send_message.return_value = MagicMock()
        mock_client.return_value.pin_message.return_value = MagicMock()

        # Create a temporary directory structure:
        # temp_dir/
        #   file_root.txt
        #   subdir/
        #     file_sub.txt
        temp_dir = tempfile.mkdtemp()
        try:
            # Use fixed names to avoid order issues if needed, though we sort in code now
            with open(os.path.join(temp_dir, 'file_root.txt'), 'w') as f:
                f.write('root content')
            
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, 'file_sub.txt'), 'w') as f:
                f.write('sub content')

            runner = CliRunner()
            # Use the temp_dir as a topic
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir])
            self.assertEqual(result.exit_code, 0, result.output)

            # send_files should be called once for the whole process
            mock_client.return_value.send_files.assert_called_once()
            args = mock_client.return_value.send_files.call_args
            files_sent = list(args[0][1])

            # Should have 2 files (file_root.txt and file_sub.txt) 
            # and 1 DirectoryMarker for subdir
            from telegram_upload.upload_files import DirectoryMarker

            # Verify order: file_root.txt first, then DirectoryMarker, then file_sub.txt
            file_names = []
            for f in files_sent:
                if isinstance(f, DirectoryMarker):
                    file_names.append('DIR:' + f.file_name)
                else:
                    file_names.append(os.path.basename(f.path))

            self.assertEqual(file_names, ['file_root.txt', 'DIR:subdir', 'file_sub.txt'])
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_topic_folder_recursive(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic
        
        async def mock_check_topic(entity, topic_id):
            return True
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic

        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            test_file = os.path.join(sub_dir, 'file.txt')
            with open(test_file, 'w') as f:
                f.write('content')

            runner = CliRunner()
            # Use the temp_dir as a topic
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir])
            self.assertEqual(result.exit_code, 0, result.output)
            
            # send_files should be called with the file from the subdir 
            # and a DirectoryMarker for the subdir
            mock_client.return_value.send_files.assert_called_once()
            args = mock_client.return_value.send_files.call_args
            files_sent = list(args[0][1])
            self.assertEqual(len(files_sent), 2)
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_topic_folder_recursive_with_sort(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_get_topic(entity, title):
            return 123
        mock_client.return_value.get_or_create_topic.side_effect = mock_get_topic

        temp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(temp_dir, 'b_root.txt'), 'w') as f:
                f.write('root')
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, 'a_sub.txt'), 'w') as f:
                f.write('sub')
            runner = CliRunner()
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir, '--sort'])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_client.return_value.send_files.assert_called_once()
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_dry_run_does_not_send_or_create(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_find_topic(entity, title):
            return None
        mock_client.return_value.find_topic.side_effect = mock_find_topic

        temp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(temp_dir, 'a.txt'), 'w') as f:
                f.write('content')
            sub_dir = os.path.join(temp_dir, 'subdir')
            os.makedirs(sub_dir)
            with open(os.path.join(sub_dir, 'b.txt'), 'w') as f:
                f.write('content')
            runner = CliRunner()
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir, '--dry-run'])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_client.return_value.get_or_create_topic.assert_not_called()
            mock_client.return_value.send_files.assert_not_called()
            mock_client.return_value.send_files_as_album.assert_not_called()
            self.assertIn('[dry-run]', result.output)
            self.assertIn('would create', result.output)
            self.assertIn('a.txt', result.output)
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_dry_run_existing_topic_with_skip(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_find_topic(entity, title):
            return 123
        mock_client.return_value.find_topic.side_effect = mock_find_topic
        mock_client.return_value.plan_files.side_effect = (
            lambda entity, files, reply_to=None, skip=False, send_as_media=False:
            [('upload', f) for f in files]
        )

        temp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(temp_dir, 'a.txt'), 'w') as f:
                f.write('content')
            runner = CliRunner()
            result = runner.invoke(upload, ['--to', 'me', '--topic', temp_dir, '--skip', '--dry-run'])
            self.assertEqual(result.exit_code, 0, result.output)
            mock_client.return_value.get_or_create_topic.assert_not_called()
            mock_client.return_value.send_files.assert_not_called()
            self.assertIn('[dry-run]', result.output)
            self.assertNotIn('would create', result.output)
            self.assertIn('a.txt', result.output)
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_topic_depth_one_expands(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        ids = {'SubA': 11, 'SubB': 22}

        async def mock_find_topic(entity, title):
            return ids.get(title, 99)
        mock_client.return_value.find_topic.side_effect = mock_find_topic
        mock_client.return_value.get_or_create_topic.side_effect = mock_find_topic

        temp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(temp_dir, 'root.txt'), 'w') as f:
                f.write('root')
            for sub in ('SubA', 'SubB'):
                sub_dir = os.path.join(temp_dir, sub)
                os.makedirs(sub_dir)
                with open(os.path.join(sub_dir, 'inner.txt'), 'w') as f:
                    f.write(sub)
            os.makedirs(os.path.join(temp_dir, 'EmptyDir'))
            runner = CliRunner()
            result = runner.invoke(
                upload, ['--to', 'me', '--topic', temp_dir, '--topic-depth', '1'])
            self.assertEqual(result.exit_code, 0, result.output)
            # General (root files) + SubA + SubB; empty dir skipped
            self.assertEqual(mock_client.return_value.send_files.call_count, 3)
            calls = mock_client.return_value.send_files.call_args_list
            self.assertIsNone(calls[0].kwargs['reply_to'])
            root_files = list(calls[0][0][1])
            self.assertEqual([os.path.basename(f.path) for f in root_files], ['root.txt'])
            by_topic = {c.kwargs['reply_to']: sorted(
                os.path.basename(f.path) for f in list(c[0][1])) for c in calls[1:]}
            self.assertEqual(by_topic, {11: ['inner.txt'], 22: ['inner.txt']})
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_topic_depth_two(self, mock_client: MagicMock, _: MagicMock):
        import tempfile
        import shutil
        from telegram_upload.upload_files import DirectoryMarker
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        ids = {'A': 1, 'A / B': 2}

        async def mock_find_topic(entity, title):
            return ids.get(title, 99)
        mock_client.return_value.find_topic.side_effect = mock_find_topic
        mock_client.return_value.get_or_create_topic.side_effect = mock_find_topic

        temp_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(temp_dir, 'root.txt'), 'w') as f:
                f.write('root')
            os.makedirs(os.path.join(temp_dir, 'A', 'B', 'C'))
            with open(os.path.join(temp_dir, 'A', 'a.txt'), 'w') as f:
                f.write('a')
            with open(os.path.join(temp_dir, 'A', 'B', 'b.txt'), 'w') as f:
                f.write('b')
            with open(os.path.join(temp_dir, 'A', 'B', 'C', 'c.txt'), 'w') as f:
                f.write('c')
            runner = CliRunner()
            result = runner.invoke(
                upload, ['--to', 'me', '--topic', temp_dir, '--topic-depth', '2'])
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(mock_client.return_value.send_files.call_count, 3)
            calls = mock_client.return_value.send_files.call_args_list
            self.assertIsNone(calls[0].kwargs['reply_to'])
            self.assertEqual(calls[1].kwargs['reply_to'], 1)
            self.assertEqual(calls[2].kwargs['reply_to'], 2)
            a_files = [os.path.basename(f.path) for f in list(calls[1][0][1])
                       if not isinstance(f, DirectoryMarker)]
            self.assertEqual(a_files, ['a.txt'])
            b_items = list(calls[2][0][1])
            b_names = ['DIR:' + f.file_name if isinstance(f, DirectoryMarker)
                       else os.path.basename(f.path) for f in b_items]
            self.assertEqual(b_names, ['b.txt', 'DIR:C', 'c.txt'])
        finally:
            shutil.rmtree(temp_dir)

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_exclusive(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(upload, ['missing_file.txt', '--thumbnail-file', 'cara128.png', '--no-thumbnail'])
        self.assertEqual(result.exit_code, 2)
        m1.return_value.send_files.assert_not_called()

    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_upload_topic_not_found_warning(self, mock_client: MagicMock, _: MagicMock):
        mock_client.return_value.max_caption_length = 200
        mock_client.return_value.max_file_size = 1024 * 1024 * 1024

        async def mock_check_topic(entity, topic_id):
            return False
        mock_client.return_value.check_topic_exists.side_effect = mock_check_topic

        test_file = os.path.join(directory, 'file1.txt')
        runner = CliRunner()
        result = runner.invoke(upload, ['--to', 'me', '--topic', '15199', test_file])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Warning: Topic ID 15199 not found', result.output)


class TestDownload(unittest.TestCase):
    @patch('telegram_upload.management.default_config')
    @patch('telegram_upload.management.TelegramManagerClient')
    def test_download(self, m1, m2):
        runner = CliRunner()
        result = runner.invoke(download, [])
        self.assertEqual(result.exit_code, 0)
        m1.assert_called_once()
        m1.return_value.download_files.assert_called_once()
