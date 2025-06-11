# Copyright (c) 2025 Christoph Hänisch.
# This file is part of the MIDI over LAN project.
# It is licensed under the GNU Lesser General Public License v3.0.
# See the LICENSE file for more details.

"""Logging setup for the MIDI over LAN GUI client.

Public API:
    - activate_logging_jsonl: Activate the JSONL logging handler.
    - start_logger_thread: Start the logger thread.
    - stop_logger_thread: Stop the logger thread.
"""

# pylint: disable=line-too-long
# pylint: disable=invalid-name

import logging
import logging.handlers
import multiprocessing
import os
import threading
import warnings

import midi_over_lan.logging_setup

logger_thread = None


class JsonLinesFormatter(logging.Formatter):
    """A custom JSON line formatter."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON line."""
        # From record.filename, extract only the file name without the path.
        filename = os.path.basename(record.filename)
        message = record.getMessage().replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        output_string = f'{{"asctime": "{self.formatTime(record, self.datefmt)}",' \
                        f'"filename": "{filename}",' \
                        f'"funcName": "{record.funcName}",' \
                        f'"levelname": "{record.levelname}",' \
                        f'"levelno": "{record.levelno}",' \
                        f'"lineno": "{record.lineno}",' \
                        f'"message": "{message}",' \
                        f'"module": "{record.module}",' \
                        f'"msecs": "{record.msecs}",' \
                        f'"name": "{record.name}",' \
                        f'"process": "{record.process}",' \
                        f'"processName": "{record.processName}",' \
                        f'"thread": "{record.thread}",' \
                        f'"threadName": "{record.threadName}",' \
                        f'"taskName": "{record.taskName}"}}'
                        # f'"pathname": "{record.pathname}",' \
        return output_string


jsonl_handler = logging.handlers.RotatingFileHandler("log messages.jsonl", encoding="utf-8", maxBytes=1000000, backupCount=5)
jsonl_handler.setFormatter(JsonLinesFormatter())
jsonl_handler.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s  %(levelname)s  %(module)-15s  line %(lineno)-4d  %(message)s')


logger = logging.getLogger("MIDI over LAN GUI")
logger.setLevel(logging.DEBUG)


def activate_logging_jsonl():
    """Activate the JSONL logging handler."""
    root = logging.getLogger()
    root.addHandler(jsonl_handler)


def start_logger_thread(log_queue:multiprocessing.Queue):
    """Start the logger thread.

    This function starts a logger thread that processes log messages from a
    log queue - a multiprocessing.Queue which is used to communicate log
    messages between worker processes and the main process. The queue must be
    created in main process and then be passed to this function. The logger
    thread should also run in the main process.

    If the queue is full, the worker processes will block until the logger thread
    has processed some log messages. This is why the function should be called
    as early as possible.

    The worker processes do call the init_logger() function from the
    midi_over_lan.logging_setup module to set up the logger. This function
    expects a log queue as an argument; it is the same queue that is passed to
    this function.
    
    The logger is named 'midi_over_lan'.

    Note: This function must be called in the main process and may only be
          called once. Before terminating the main process, the logger thread
          must be stopped by calling stop_logger_thread().
    """
    global logger_thread  # pylint: disable=global-statement
    logger_thread = threading.Thread(target=midi_over_lan.logging_setup.logger_thread, args=(log_queue,))
    logger_thread.start()
    return logger_thread


def stop_logger_thread(log_queue:multiprocessing.Queue) -> None:
    """Stop the logger thread.
    
    Note, the log queue passed to this function must be the same queue that was
    passed to the start_logger_thread() function.
    """
    log_queue.put(None)  # Stop the logger thread (by protocol) by putting a None object into the queue.
    if logger_thread:
        logger_thread.join()
    else:
        warnings.warn("Logger thread was not started. Nothing to stop.")
