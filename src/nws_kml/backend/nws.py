# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

import logging
from typing import Any

import aiohttp
from fastapi import HTTPException

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

    for state in STATES:
        if state in cfg.fetching.states_ignore:
            continue
        else:
            logger.info(f"on state: {state}")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{BASE_URL}/stations?state={state}&limit={limit}"
                ) as response:
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
    if len(_station_ids) > 0:
        return _station_ids
    
    # fill _station_ids using the NWS API response
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_URL}/stations"
        ) as response:
            response_json = await response.json()
            stations = response_json.get("features")
            station_urls = [station.get("id") for station in stations]
            station_ids = [station_url.split("/")[-1] for station_url in station_urls]

            _station_ids = station_ids
            return _station_ids
        

async def get_station_observation_latest(
    station_id: int,
) -> dict[str, Any]:
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
            f"{BASE_URL}/stations/{station_id}/observations/latest"
        ) as response:
            return await response.json()
        

async def get_stations_observation_latest() -> list[dict[str, Any]]:
    """
    Get the latest observation data for all current supported stations.
    """
    global _station_ids
    observations: list[dict[str, Any]] = []
    for station_id in _station_ids:
        observation = await get_station_observation_latest(station_id)
        observations.append(observation)

    return observations