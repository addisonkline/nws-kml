# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

import logging


logger = logging.getLogger()


def init_logger(
    log_file_path: str = "nwskml.log",
    log_level_file: str = "INFO",
    log_level_console: str = "INFO",
) -> None:
    """
    Initialize the logger.
    """
    format = "%(asctime)s [%(levelname)s] - %(name)s - %(message)s"
    formatter = logging.Formatter(format)

    # file handler
    logging.basicConfig(
        filename=log_file_path,
        format=format,
        level=log_level_file
    )

    # stream (console) handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level_console)
    logger.addHandler(console_handler)

    logger.info(f"initialized logger with filepath = {log_file_path}, file_level = {log_level_file}, console_level = {log_level_console}")
