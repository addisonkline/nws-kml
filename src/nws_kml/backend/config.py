# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Addison Kline

from pydantic import BaseModel
from tomlkit import (
    TOMLDocument,
    comment,
    document,
    nl,
    table,
    loads
)
from tomlkit.container import Container
from tomlkit.items import (
    Table,
    Item
)


class FetchingConfig(BaseModel):
    """
    Configuration model for options for fetching from the NWS API.
    """
    query_limit: int = 20
    query_cooldown: float = 0.2
    states_ignore: list[str] = []
    continue_on_5xx: bool = False

    def to_toml_table(self) -> Table:
        """
        Convert this to a TOML table.
        """
        fetching = table()

        fetching.add("query_limit", self.query_limit)
        fetching["query_limit"].comment("number of station IDs to query per state")
        fetching.add("query_cooldown", self.query_cooldown)
        fetching["query_cooldown"].comment("number of seconds between NWS API requests")
        fetching.add("states_ignore", self.states_ignore)
        fetching["states_ignore"].comment("list of states by ID to exclude (e.g. ['CA', 'DC', 'IL'])")
        fetching.add("continue_on_5xx", self.continue_on_5xx)

        return fetching
    
    @staticmethod
    def from_toml(toml_table: Item | Container) -> "FetchingConfig":
        """
        Build this config model from a TOML string.
        """
        query_limit = toml_table["query_limit"] # type: ignore
        query_cooldown = toml_table["query_cooldown"] # type: ignore
        states_ignore = toml_table["states_ignore"] # type: ignore
        continue_on_5xx = toml_table["continue_on_5xx"] # type: ignore

        return FetchingConfig(
            query_limit=query_limit, # type: ignore
            query_cooldown=query_cooldown, # type: ignore
            states_ignore=states_ignore, # type: ignore
            continue_on_5xx=continue_on_5xx # type: ignore
        )


class DisplayConfig(BaseModel):
    """
    Configuration model for options for exposing KML points via the server.
    """
    require_temperature: bool = True
    require_dew_point: bool = True
    require_pressure_barometric: bool = False
    require_pressure_sea_level: bool = False
    require_wind_direction: bool = True
    require_wind_speed: bool = True
    require_wind_gust: bool = False

    def to_toml_table(self) -> Table:
        """
        Convert this to a TOML table.
        """
        display = table()
        display.comment("configure which weather params are required for a given station in the KML")

        display.add("require_temperature", self.require_temperature)
        display.add("require_dew_point", self.require_dew_point)
        display.add("require_pressure_barometric", self.require_pressure_barometric)
        display.add("require_pressure_sea_level", self.require_pressure_sea_level)
        display.add("require_wind_direction", self.require_wind_direction)
        display.add("require_wind_speed", self.require_wind_speed)
        display.add("require_wind_gust", self.require_wind_gust)

        return display
    
    @staticmethod
    def from_toml(toml_table: Item | Container) -> "DisplayConfig":
        """
        Build this config model from a TOML string.
        """
        require_temperature = toml_table["require_temperature"] # type: ignore
        require_dew_point = toml_table["require_dew_point"] # type: ignore
        require_pressure_barometric = toml_table["require_pressure_barometric"] # type: ignore
        require_pressure_sea_level = toml_table["require_pressure_sea_level"] # type: ignore
        require_wind_direction = toml_table["require_wind_direction"] # type: ignore
        require_wind_speed = toml_table["require_wind_speed"] # type: ignore
        require_wind_gust = toml_table["require_wind_gust"] # type: ignore

        return DisplayConfig(
            require_temperature=require_temperature, # type: ignore
            require_dew_point=require_dew_point, # type: ignore
            require_pressure_barometric=require_pressure_barometric, # type: ignore
            require_pressure_sea_level=require_pressure_sea_level, # type: ignore
            require_wind_direction=require_wind_direction, # type: ignore
            require_wind_speed=require_wind_speed, # type: ignore
            require_wind_gust=require_wind_gust # type: ignore
        )


class NwskmlConfig(BaseModel):
    """
    Configuration model for NWSKML.
    """
    fetching: FetchingConfig = FetchingConfig()
    display: DisplayConfig = DisplayConfig()

    def to_toml(self) -> TOMLDocument:
        """
        Convert this config object into a valid TOML document.
        """
        doc = document()
        doc.add(comment("nwskml configuration file (auto-generated)"))
        doc.add(nl())

        doc.add("fetching", self.fetching.to_toml_table())
        doc.add("display", self.display.to_toml_table())

        return doc
    
    @staticmethod
    def from_toml(toml_str: str) -> "NwskmlConfig":
        """
        Build this config model from a TOML string.
        """
        doc = loads(toml_str)

        fetching = FetchingConfig.from_toml(doc["fetching"])
        display = DisplayConfig.from_toml(doc["display"])

        return NwskmlConfig(
            fetching=fetching,
            display=display
        )
    

def read_config_file() -> NwskmlConfig:
    """
    Read an existing `nwskml.toml` file and create an `NwskmlConfig` object.
    """
    with open("nwskml.toml") as file:
        content = file.read()
        return NwskmlConfig.from_toml(content)

