# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

import logging
from importlib import metadata
from time import sleep
from typing import Any

import aiohttp
from fastapi import HTTPException
from tqdm import tqdm

from nws_kml.backend.config import NwskmlConfig
from nws_kml.backend.constants import STATES


logger = logging.getLogger(__name__)

BASE_URL = "https://api.weather.gov"

_station_ids: list[int] = []


async def populate_station_ids(
    cfg: NwskmlConfig,
):
    """
    Populate the field `_station_ids` to avoid repeated calls later.
    """
    logger.info("populating NWS station IDs...")
    global _station_ids

    limit = cfg.fetching.query_limit

    for state in tqdm(STATES, desc="getting station IDs by state"):
        if state in cfg.fetching.states_ignore:
            continue
        else:
            sleep(cfg.fetching.query_cooldown)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BASE_URL}/stations?state={state}&limit={limit}",
                    headers={
                        "User-Agent": get_user_agent()
                    }
                ) as response:
                    if (cfg.fetching.continue_on_5xx) and (response.status >= 500) and (response.status < 600):
                        continue
                    response_json = await response.json()
                    stations = response_json.get("features")
                    station_urls = [station.get("id") for station in stations]
                    station_ids = [station_url.split("/")[-1] for station_url in station_urls]

                    _station_ids.extend(station_ids)
                    
    logger.info(f"finished populating NWS station IDs (n = {len(_station_ids)})")


async def get_station_ids(
    cfg: NwskmlConfig,
) -> list[int]:
    """
    Get a list of current NWS station IDs.
    """
    global _station_ids
    if len(_station_ids) == 0:
        await populate_station_ids(cfg)

    return _station_ids
        

async def get_station_observation_latest(
    station_id: int,
) -> dict[str, Any] | None:
    """
    Get the latest observation data for the given station.
    """
    global _station_ids
    if station_id not in _station_ids:
        raise HTTPException(
            status_code=404,
            detail="station with given ID not found"
        )
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_URL}/stations/{station_id}/observations/latest",
            headers={
                "User-Agent": get_user_agent()
            }
        ) as response:
            if (response.status >= 500) and (response.status < 600):
                return None
            return await response.json()


def get_user_agent() -> str:
    """
    Create the `User-Agent` field for HTTP requests to the NWS API.
    """
    version = metadata.version("nws-kml")
    return f"nws-kml/{version} (https://github.com/addisonkline/nws-kml)"