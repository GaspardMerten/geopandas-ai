# GeoPandas AI

GeoPandas AI is a powerful Python library that brings natural language processing capabilities to your geospatial data
analysis workflow. It allows you to interact with GeoDataFrames using natural language queries, making geospatial
analysis more accessible and intuitive.

## Features

- Natural language interaction with GeoDataFrames
- Support for multiple LLM providers through LiteLLM
- Various output types including:
    - GeoDataFrames
    - DataFrames
    - Text responses
    - Plots
    - Interactive maps
    - Lists
    - Dictionaries
    - Numeric values (integers, floats)
    - Boolean values

## Installation

```bash
pip install geopandas-ai
```

## Quick Start

```python
import geopandasai as gpdai

# Configure your LLM provider (example using Google's Vertex AI)
gpdai.set_active_lite_llm_config({
    "model": "vertex_ai/gemini-2.0-flash",
    "vertex_credentials": json.dumps(json.load(open("google-credentials.json", "r")))
})

# Load your geospatial data
gdfai = gpdai.read_file("your_data.geojson")

# Ask questions about your data
result = gdfai.chat("how many points are in this dataset?")
print(result)

# Get specific types of results
count = gdfai.chat("how many points?", result_type=gpdai.ResultType.INTEGER)
points_only = gdfai.chat("Keep only geometry of type point", result_type=gpdai.ResultType.GEODATAFRAME)
map_view = gdfai.chat("Plot the points", result_type=gpdai.ResultType.MAP)
```

## Configuration

GeoPandas AI uses LiteLLM to support multiple LLM providers. You can configure your preferred provider in two ways:

1. Using the `set_active_lite_llm_config` function:

```python
from geopandasai.config import set_active_lite_llm_config

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

GeoPandas AI allows you to extend its capabilities by adding custom libraries that can be used in the generated code. There are two ways to add libraries:

1. Globally using `set_libraries`:
```python
from geopandasai.config import set_libraries

# Add libraries that will be available for all chat queries
set_libraries(['numpy', 'scipy', 'shapely'])
```

2. Per-query using the `user_provided_libraries` parameter:
```python
# Add libraries for a specific query
result = gdfai.chat(
    "calculate the convex hull using scipy",
    result_type=ResultType.GEODATAFRAME,
    user_provided_libraries=['scipy', 'numpy']
)
```

By default, the following libraries are always available:
- pandas
- matplotlib.pyplot
- folium
- geopandas

Note: Make sure any additional libraries you specify are installed in your environment.

## Available Result Types

The library supports various result types through the `ResultType` enum:

- `DATAFRAME`: Returns a pandas DataFrame
- `GEODATAFRAME`: Returns a GeoDataFrame
- `TEXT`: Returns a text response
- `PLOT`: Returns a matplotlib figure
- `MAP`: Returns a folium map
- `LIST`: Returns a list
- `DICT`: Returns a dictionary
- `INTEGER`: Returns an integer
- `FLOAT`: Returns a float
- `BOOLEAN`: Returns a boolean

## Examples

### Basic Queries

```python
# Count features
count = gdfai.chat("how many features?", result_type=ResultType.INTEGER)

# Filter data
filtered = gdfai.chat("show only points with population > 1000", result_type=ResultType.GEODATAFRAME)

# Get statistics
stats = gdfai.chat("what's the average population?", result_type=ResultType.FLOAT)
```

### Visualization

```python
# Create a plot
plot = gdfai.chat("create a scatter plot of population vs area", result_type=ResultType.PLOT)

# Generate an interactive map
map = gdfai.chat("show all points colored by population", result_type=ResultType.MAP)
```

### Data Transformation

```python
# Convert to list
list_data = gdfai.chat("convert to list", result_type=ResultType.LIST)

# Convert to dictionary
dict_data = gdfai.chat("convert to json", result_type=ResultType.DICT)
```

## Caching

GeoPandas AI includes a caching system to improve performance and reduce API calls. The library provides two types of
caches:

1. `InMemoryResultCache`: Stores results in memory (default)
2. `FileResultCache`: Persists results to disk

### Using Caching

```python
from geopandasai import set_cache_instance, FileCache, InMemoryCache

# Use in-memory cache (default)
set_cache_instance(InMemoryCache())

# Or use file-based cache
set_cache_instance(FileCache(cache_dir="./.geopandasai_cache"))
```

The cache automatically stores:

- Query results
- Generated code
- Any intermediate results

This helps in:

- Reducing API calls
- Improving response times for repeated queries
- Saving costs when using paid LLM providers

## Accessing Generated Code

After each query, you can access the generated Python code that was used to produce the result:

```python
# Make a query
result = gdfai.chat("how many points are in this dataset?")

# Access the generated code
print(gdfai.last_output.source_code)
```

This is useful for:

- Understanding how the AI interpreted your query
- Learning from the generated code
- Debugging unexpected results
- Reusing the generated code in your own scripts

## Requirements

- Python 3.8+
- GeoPandas
- LiteLLM
- Matplotlib
- Folium

## License

MIT + Commercial Platform Restriction (see LICENSE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 