import shutil
from ctypes import c_int64

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

    def progress(current, total):
        if current < last_current.value:
            return
        # Clear the current line to handle terminal resize ghosting
        click.echo('\r\033[2K', nl=False)
        # Recalculate label and update progress
        bar.label = get_label()
        bar.pos = 0
        bar.update(current)
        last_current.value = current
    return progress, bar
