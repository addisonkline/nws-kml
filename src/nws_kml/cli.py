# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Addison Kline

import argparse

from nws_kml.server import run_server
from nws_kml.utils import (
    print_version,
    write_config
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="nwskml",
        description="Server for NWS weather data in KML format." \
        " Accessible in Google Earth Pro via the Network Link feature",
        epilog="Copyright (c) 2025-present Addison Kline (GitHub: @addisonkline)"
    )
    subparsers = parser.add_subparsers(title="subcommands")

    # serve parser: run the nwskml server
    serve_parser = subparsers.add_parser(
        "serve",
        aliases=["s"],
        help="run the nwskml server"
    )
    serve_parser.add_argument(
        "-H",
        "--host",
        default="0.0.0.0",
        help="the host to run the server on (default: '0.0.0.0')"
    )
    serve_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8020,
        help="the port to run the server on (default: 8020)"
    )
    serve_parser.add_argument(
        "-lf",
        "--log-file",
        default="nwskml.log",
        help="the log file to write to (default: 'nwskml.log')"
    )
    serve_parser.add_argument(
        "-llf",
        "--log-level-file",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="the minimum log level to write to the file (default: 'INFO')"
    )
    serve_parser.add_argument(
        "-llc",
        "--log-level-console",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="the minimum log level to write to stderr (default: 'INFO')"
    )
    serve_parser.set_defaults(func=run_server)

    # config parser: create the config file "nwskml.toml"
    config_parser = subparsers.add_parser(
        "config",
        aliases=["c"],
        help="create a new config file 'nwskml.toml'"
    )
    config_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite an existing 'nwskml.toml' file"
    )
    config_parser.set_defaults(func=write_config)

    # version parser: just get the software version
    version_parser = subparsers.add_parser(
        "version",
        aliases=["V"],
        help="print the software version and exit"
    )
    version_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="include more detailed software information"
    )
    version_parser.set_defaults(func=print_version)

    args = parser.parse_args()

    args.func(args)