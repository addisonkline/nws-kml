# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Addison Kline

import logging
from contextlib import asynccontextmanager
from argparse import Namespace

from fastapi import FastAPI, Response
import uvicorn

from nws_kml.backend.config import read_config_file
from nws_kml.backend.kml import (
    populate_kml,
    get_kml_http_response,
    refresh_kml
)
from nws_kml.backend.nws import populate_station_ids
from nws_kml.logger import init_logger
from nws_kml.utils import get_version
from nws_kml import types


logger = logging.getLogger(__name__)


async def _server_startup(app: FastAPI):
    """
    Handle the server startup process.
    """
    logger.info("server starting up...")

    app.state.cfg = read_config_file()
    await populate_station_ids(app.state.cfg)
    await populate_kml(app.state.cfg)

    logger.info("server startup complete")


async def _server_shutdown(app: FastAPI):
    """
    Handle the server shutdown process.
    """
    logger.info("server shutting down...")

    logger.info("server shutdown complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle server startup and shutdown events.
    """
    await _server_startup(app)

    yield

    await _server_shutdown(app)


app = FastAPI(lifespan=lifespan)


@app.get("/", response_model=types.GetRootResponse)
async def get_root() -> types.GetRootResponse:
    """
    `GET /`: Get basic server info and metadata.
    """
    return types.GetRootResponse(
        name="nwskml",
        version=get_version(),
        status="ok"
    )


@app.get("/kml")
async def get_kml() -> Response:
    """
    `GET /kml`: Get the NWS station observation info as KML.
    """
    return await get_kml_http_response()


@app.post("/refresh")
async def post_refresh():
    """
    `POST /refresh`: Update existing station observation data.
    """
    await refresh_kml(app.state.cfg)


def run_server(
    args: Namespace,
) -> None:
    """
    Run the server via the CLI.
    """
    host = args.host
    port = args.port
    log_file = args.log_file
    log_level_file = args.log_level_file
    log_level_console = args.log_level_console

    init_logger(
        log_file_path=log_file,
        log_level_file=log_level_file,
        log_level_console=log_level_console
    )

    uvicorn.run(
        "nws_kml.server:app",
        host=host,
        port=port,
        log_config=None,
    )
