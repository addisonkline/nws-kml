# nws-kml

See weather data in Google Earth, provided by the National Weather Service (NWS) API over network link. Like it's 2012 all over again.

## Quickstart

To use `nws-kml`, ensure you have Python version 3.12 or higher, `git`, `uv` (the Python package manager), and Google Earth Pro installed.

Start by cloning this repo:

```bash
git clone https://github.com/addisonkline/nws-kml
```

Then go to the `nws-kml` directory and sync the Python dependencies:

```bash
cd nws-kml
uv sync
```

To start the `nws-kml` server, ensure you have a `nwskml.toml` file in the project root. Then, run:

```bash
uv run nwskml serve # port 8020 by default; change with `--port`
```

The server startup process takes several minutes to fetch the relevant data from the NWS API. Once the server startup completes, you can connect it via network link to Google Earth.

In Google Earth Pro, add a new network link from the top left toolbar: `Add -> Network Link`. Set the value of the Link field to `http://localhost:8020/kml`.

The weather stations may not appear at first--in which case, refresh the network link and they should pop up.

## Limitations

- Only weather stations in the United States (50 states + DC) are currently supported.
- All weather stations (based on the specified configuration) are fetched on server startup, rather than intelligently fetched based on the Google Earth window box.

## Acknowledgements

`nws-kml` would not be possible without the National Weather Service's public API (https://api.weather.gov), the free API for accessing weather data provided by the U.S. government.