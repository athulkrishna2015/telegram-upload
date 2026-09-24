import shutil
import time
from ctypes import c_int64, c_double

import click

from telegram_upload.utils import truncate


def get_progress_bar(action, file, length):
    def get_label():
        columns, _ = shutil.get_terminal_size()
        # Leave space for the bar and percentages (around 45 chars)
        max_label_length = max(columns - 45, 20)
        label = '{} "{}"'.format(action, file)
        return truncate(label, max_label_length)

    bar = click.progressbar(label=get_label(), length=length)
    last_current = c_int64(0)
    last_update_time = c_double(0)
    update_interval = 0.1  # 10Hz

    def progress(current, total):
        now = time.time()
        # Throttle updates to avoid flickering, but always update at 0% and 100%
        # total can be None if unknown
        is_end = total is not None and current >= total
        if (not is_end and current > 0 and 
                now - last_update_time.value < update_interval and
                current > last_current.value):
            return

        if current < last_current.value:
            return

        # Clear the current line to handle terminal resize ghosting
        click.echo('\r\033[2K', nl=False)
        # Recalculate label and update progress
        bar.label = get_label()
        bar.pos = 0
        bar.update(current)
        
        last_current.value = current
        last_update_time.value = now
    return progress, bar
