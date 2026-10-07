import unittest
from unittest.mock import patch, MagicMock

from telegram_upload.client.progress_bar import get_progress_bar, format_duration


class TestFormatDuration(unittest.TestCase):
    def test_format_duration(self):
        self.assertEqual(format_duration(0), '0:00')
        self.assertEqual(format_duration(61), '1:01')
        self.assertEqual(format_duration(3661), '1:01:01')


class TestProgressLine(unittest.TestCase):
    @patch("telegram_upload.client.progress_bar.click")
    @patch("telegram_upload.client.progress_bar.shutil.get_terminal_size", return_value=(120, 30))
    def test_renders_counter_and_percent(self, mock_size: MagicMock, mock_click: MagicMock):
        progress, line = get_progress_bar('Uploading', 'a.mp4', 100, position=(3, 10))
        progress(50, 100)
        progress(30, 100)  # The bar should not go back
        self.assertEqual(mock_click.echo.call_count, 1)
        rendered = mock_click.echo.call_args[0][0]
        self.assertIn('[3/10]', rendered)
        self.assertIn('50%', rendered)
        self.assertIn('a.mp4', rendered)

    @patch("telegram_upload.client.progress_bar.click")
    @patch("telegram_upload.client.progress_bar.shutil.get_terminal_size", return_value=(120, 30))
    def test_render_finish_prints_checkmark(self, mock_size: MagicMock, mock_click: MagicMock):
        progress, line = get_progress_bar('Uploading', 'a.mp4', 100, position=(1, 1))
        progress(100, 100)
        line.render_finish()
        line.render_finish()  # Second finish is a no-op
        finish = mock_click.echo.call_args[0][0]
        self.assertIn('✓', finish)
        self.assertIn('a.mp4', finish)

    @patch("telegram_upload.client.progress_bar.click")
    @patch("telegram_upload.client.progress_bar.shutil.get_terminal_size", return_value=(120, 30))
    def test_no_position_renders_without_counter(self, mock_size: MagicMock, mock_click: MagicMock):
        progress, _ = get_progress_bar('Uploading', 'a.mp4', 100)
        progress(100, 100)
        rendered = mock_click.echo.call_args[0][0]
        self.assertIn('Uploading "a.mp4"', rendered)
        self.assertNotIn('[1/1]', rendered)
