import unittest
from unittest.mock import MagicMock, patch
from telethon import types
import os
import sys

# Mocking modules that might be missing or hard to initialize
sys.modules['hachoir'] = MagicMock()
sys.modules['hachoir.metadata'] = MagicMock()
sys.modules['hachoir.metadata.metadata'] = MagicMock()
sys.modules['hachoir.metadata.video'] = MagicMock()

from telegram_upload.client.telegram_upload_client import TelegramUploadClient
from telegram_upload.upload_files import File

class TestRepro(unittest.TestCase):
    @patch('telegram_upload.client.telegram_upload_client.TelegramClient.__init__', return_value=None)
    def test_repro_typeerror(self, m1):
        client = TelegramUploadClient(None, None, None)
        client.loop = MagicMock()
        
        # This is what Telethon's utils.get_message_id does:
        from telethon import utils
        
        reply_to = types.InputReplyToMessage(reply_to_msg_id=123, top_msg_id=123)
        
        print(f"Testing with type: {type(reply_to)}")
        try:
            utils.get_message_id(reply_to)
            print("Successfully got message id (unexpected)")
        except TypeError as e:
            print(f"Caught expected TypeError: {e}")

if __name__ == '__main__':
    unittest.main()
