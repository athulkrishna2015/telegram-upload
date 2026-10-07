import shutil
import time

import click

from telegram_upload.utils import truncate, sizeof_fmt


BAR_WIDTH = 20
UPDATE_INTERVAL = 0.1  # 10Hz


def format_duration(seconds):
    seconds = max(int(seconds), 0)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if hours:
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    return f'{minutes}:{seconds:02d}'


class ProgressLine:
    """Single updating status line: counter, percent, bar, sizes, rate and ETA."""

    def __init__(self, action, file, length, position=None):
        self.action = action
        self.file = file
        self.length = length or 0
        self.position = position
        self.started = time.time()
        self.last_render = 0.0
        self.last_current = 0
        self.finished = False

    @property
    def counter(self):
        if not self.position:
            return ''
        index, total = self.position
        return f'[{index}/{total}] '

    def _numbers(self, current):
        total = self.length
        done = sizeof_fmt(current, suffix='B')
        if total:
            return f'{done}/{sizeof_fmt(total, suffix="B")}'
        return done

    def _rate_eta(self, current, elapsed):
        if elapsed <= 0 or current <= 0:
            return ''
        rate = current / elapsed
        parts = [f'{sizeof_fmt(rate, suffix="B")}/s']
        if self.length and rate > 0:
            remaining = max(self.length - current, 0)
            parts.append(f'ETA {format_duration(remaining / rate)}')
        return ' · '.join(parts)

    def render(self, current, total=None):
        now = time.time()
        is_end = self.length and current >= self.length
        if (not is_end and current > 0
                and now - self.last_render < UPDATE_INTERVAL
                and current > self.last_current):
            return
        if current < self.last_current:
            return
        self.last_current = current
        self.last_render = now
        columns, _ = shutil.get_terminal_size()
        percent = f'{100 * current / self.length:3.0f}%' if self.length else '--%'
        numbers = self._numbers(current)
        extra = self._rate_eta(current, now - self.started)
        filled = int(BAR_WIDTH * current / self.length) if self.length else 0
        bar = '█' * filled + '░' * (BAR_WIDTH - filled)
        suffix = f' {percent} |{bar}| {numbers}'
        if extra:
            suffix += f' {extra}'
        max_prefix = max(columns - len(suffix) - 1, 10)
        prefix = truncate(f'{self.action} {self.counter}"{self.file}"', max_prefix)
        click.echo(f'\r\033[2K{prefix}{suffix}', nl=False)

    def update(self, current, total=None):
        self.render(current, total)

    def render_finish(self):
        if self.finished:
            return
        self.finished = True
        elapsed = time.time() - self.started
        size = sizeof_fmt(self.last_current or self.length, suffix='B')
        click.echo(f'\r\033[2K✓ {self.counter}"{self.file}" — {size} in {format_duration(elapsed)}')


def get_progress_bar(action, file, length, position=None):
    """Return (progress_callback, line) using the new single-line renderer."""
    line = ProgressLine(action, file, length, position)
    return line.update, line
