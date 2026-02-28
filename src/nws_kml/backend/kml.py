# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

import logging
from typing import Any

import simplekml # type: ignore
from fastapi import Response

from nws_kml.backend.config import NwskmlConfig
from nws_kml.backend.nws import (
    get_station_observation_latest,
    get_station_ids
)


KML_MIME = "application/vnd.google-earth.kml+xml"

logger = logging.getLogger(__name__)

_kml: simplekml.Kml = None # type: ignore


async def populate_kml(
    cfg: NwskmlConfig,
):
    """
    Populate the field `_kml` to avoid repeated calls later.
    """
    logger.info("populating KML...")

    global _kml
    station_ids = await get_station_ids(cfg)

    _kml = simplekml.Kml()
    successes = 0
    for station_id in station_ids:
        station_data = await get_station_observation_latest(station_id)

        try:
            _kml.newpoint(
                name=_generate_point_name(station_data),
                coords=_generate_point_coordinates(station_data),
                description=_generate_point_description(cfg, station_data)
            )
            successes += 1
        except RuntimeError:
            logger.warning(f"could not parse observation data from station with ID = {station_id}, continuing")
            continue
        except ValueError:
            # only thrown when configured minimums aren't met
            continue

    logger.info(f"finished populating KML ({successes}/{len(station_ids)})")


async def refresh_kml(
    cfg: NwskmlConfig
):
    """
    Refresh the existing KML file.
    """
    logger.info("populating KML...")

    global _kml
    station_ids = await get_station_ids(cfg)

    kml_new = simplekml.Kml()
    successes = 0
    for station_id in station_ids:
        station_data = await get_station_observation_latest(station_id)

        try:
            kml_new.newpoint(
                name=_generate_point_name(station_data),
                coords=_generate_point_coordinates(station_data),
                description=_generate_point_description(cfg, station_data)
            )
            successes += 1
        except RuntimeError:
            logger.warning(f"could not parse observation data from station with ID = {station_id}, continuing")
            continue
        except ValueError:
            # only thrown when configured minimums aren't met
            continue

    _kml = kml_new
    logger.info(f"finished populating KML ({successes}/{len(station_ids)})")


async def get_kml_http_response() -> Response:
    """
    Get the current KML document as an HTTP response object.
    """
    global _kml

    return Response(
        headers={"Content-Type": KML_MIME},
        content=_kml.kml()
    )


def _generate_point_name(
    data: dict[str, Any]
) -> str:
    """
    Create a valid KML point name for the given station observation data.
    """
    properties = data.get("properties")
    if properties is None:
        raise RuntimeError("station observation properties is None")
    if not isinstance(properties, dict):
        raise RuntimeError("station observation properties must be a dict")
    
    station_name = properties.get("stationName")
    if station_name is None:
        raise RuntimeError("station observation properties.stationName is None")
    
    station_id = properties.get("stationId")
    if station_id is None:
        raise RuntimeError("station observation properties.stationId is None")

    return f"{station_name} ({station_id})"


def _generate_point_coordinates(
    data: dict[str, Any]
) -> list[tuple[Any, Any]]:
    """
    Create a valid KML point coordinates list (size 1) for the given observation data.
    """
    geometry = data.get("geometry")
    if geometry is None:
        raise RuntimeError("station observation geometry is None")
    if not isinstance(geometry, dict):
        raise RuntimeError("station observation geometry must be a dict")
    
    coordinates = geometry.get("coordinates")
    if coordinates is None:
        raise RuntimeError("station observation geometry.coordinates is None")
    if not isinstance(coordinates, list):
        raise RuntimeError("station observation geometry.coordinates must be a list")
    
    return [(coordinates[0], coordinates[1])]


def _generate_point_description(
    cfg: NwskmlConfig,
    data: dict[str, Any]
) -> str:
    """
    Create a valid KML point description for the given station observation data.
    """
    properties = data.get("properties")
    if properties is None:
        raise RuntimeError("station observation properties is None")
    if not isinstance(properties, dict):
        raise RuntimeError("station observation properties must be a dict")
    
    timestamp = properties.get("timestamp")

    temperature = properties.get("temperature")
    if temperature is None:
        raise RuntimeError("station observation properties.temperature is None")
    if not isinstance(temperature, dict):
        raise RuntimeError("station observation properties.temperature must be a dict")
    
    temp_val = temperature.get("value")
    temp_unit = temperature.get("unitCode")
    if (cfg.display.require_temperature) and (temp_val is None):
        raise ValueError("temperature required but not found")

    dewpoint = properties.get("dewpoint")
    if dewpoint is None:
        raise RuntimeError("station observation properties.dewpoint is None")
    if not isinstance(dewpoint, dict):
        raise RuntimeError("station observation properties.dewpoint must be a dict")
    
    dewpoint_val = dewpoint.get("value")
    dewpoint_unit = dewpoint.get("unitCode")
    if (cfg.display.require_dew_point) and (dewpoint_val is None):
        raise ValueError("dew point required but not found")

    barometric = properties.get("barometricPressure")
    if barometric is None:
        raise RuntimeError("station observation properties.barometricPressure is None")
    if not isinstance(barometric, dict):
        raise RuntimeError("station observation properties.barometricPressure must be a dict")
    
    barometric_val = barometric.get("value")
    barometric_unit = barometric.get("unitCode")
    if (cfg.display.require_pressure_barometric) and (barometric_val is None):
        raise ValueError("barometric pressure required but not found")

    sealevel = properties.get("seaLevelPressure")
    if sealevel is None:
        raise RuntimeError("station observation properties.seaLevelPressure is None")
    if not isinstance(sealevel, dict):
        raise RuntimeError("station observation properties.seaLevelPressure must be a dict")
    
    sealevel_val = sealevel.get("value")
    sealevel_unit = sealevel.get("unitCode")
    if (cfg.display.require_pressure_sea_level) and (sealevel_val is None):
        raise ValueError("sea level pressure required but not found")

    desc = f"""
Timestamp: {timestamp}
Temperature: {temp_val} {temp_unit}
Dew Point: {dewpoint_val} {dewpoint_unit}
Pressure (Barometric): {barometric_val} {barometric_unit}
Pressure (Sea Level): {sealevel_val} {sealevel_unit}
"""
    
    return desc