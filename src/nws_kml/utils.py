# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

import os

from argparse import Namespace
from importlib import metadata
from tomlkit import dumps

from nws_kml.backend.config import NwskmlConfig


def get_version() -> str:
    """
    Get the program version using importlib.metadata.
    """
    return metadata.version("nws-kml")


def print_version(
    args: Namespace,
) -> None:
    """
    Print the program version before exiting.
    """
    version = get_version()
    print(f"nwskml version: {version}")

    if args.verbose:
        print()
        print("Copyright (c) 2025-present Addison Kline")
        print("  GitHub: @addisonkline")
        print("  Website: https://www.addisonkline.net")
        print("License: MIT")
        print("  See 'LICENSE' in the project root")


def write_config(
    args: Namespace,
) -> None:
    """
    Create a new config file `nwskml.toml`.
    Only overwrite an existing file if specified.
    """
    overwrite = args.overwrite
    exists = os.path.exists("nwskml.toml")

    if exists and not overwrite:
        print("cannot create a new config file; one already exists")
        print("to overwrite an existing config file, run with option '--overwrite'")
        print("(e.g. 'nwskml config --overwrite')")
        return
    
    toml_obj = NwskmlConfig().to_toml()
    with open("nwskml.toml", "w") as file:
        toml_str = dumps(toml_obj)
        file.write(toml_str)

    print("successfully wrote new config file 'nwskml.toml'")