# GeoPandas AI

GeoPandas AI is a powerful Python library that brings natural language processing capabilities to your geospatial data
analysis workflow. It allows you to interact with GeoDataFrames using natural language queries, making geospatial
analysis more accessible and intuitive.

## Features

- Natural language interaction with GeoDataFrames
- Support for multiple LLM providers through LiteLLM
- Built-in support for Jupyter notebooks

## Installation

```bash
pip install geopandas-ai
```

## Quick Start

GeoPandas AI is designed to work seamlessly with GeoPandas. Most function available in GeoPandas are also available in
GeoPandas AI. 

### Example Usage 1 

```python
import geopandasai as gpdai

gdfai = gpdai.read_file("path/to/your/geodatafile.geojson")

gdfai.chat("Plot the data")
gdfai.improve("Change the title to something more selling and add a basemap")
```

## Example Usage 2
```python
import geopandasai as gpdai

gdfai = gpdai.read_file("path/to/your/geodatafile.geojson")

gdfai.chat("Plot the data").chat("Change the title to something more selling and add a basemap")
```

## Configuration

GeoPandas AI uses LiteLLM to support multiple LLM providers. You can configure your preferred provider in two ways:

1. Using the `set_active_lite_llm_config` function:

```python
from geopandasai import set_active_lite_llm_config

set_active_lite_llm_config({
    "model": "your_model_name",
    # Add provider-specific configuration
})
```

2. Using environment variables:

```bash
export LITELLM_CONFIG='{"model": "your_model_name", ...}'
```

Please refer to https://docs.litellm.ai/docs/providers for more details on configuring LiteLLM.

## Adding Custom Libraries

GeoPandas AI allows you to extend its capabilities by adding custom libraries that can be used in the generated code.
There are two ways to add libraries:

1. Globally using `set_libraries`:

```python
from geopandasai import set_libraries

# Add libraries that will be available for all chat queries
set_libraries(['numpy', 'scipy', 'shapely'])
```

2. Per-query using the `user_provided_libraries` parameter:

```python
# Add libraries for a specific query
result = gdfai.chat(
    "calculate the convex hull using scipy",
    user_provided_libraries=['scipy', 'numpy']
)
```

By default, the following libraries are always available:

- pandas
- matplotlib.pyplot
- folium
- geopandas
- contextily

Note: Make sure any additional libraries you specify are installed in your environment.

## Requirements

- Python 3.8+
- GeoPandas
- LiteLLM
- Matplotlib
- Folium
- Contextily

## License

MIT + Commercial Platform Restriction (see LICENSE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 