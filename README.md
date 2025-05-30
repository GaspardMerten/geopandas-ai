<img src="https://raw.githubusercontent.com/GaspardMerten/geopandas-ai/main/logo.avif" alt="GeoPandas AI Logo" width="200">

# GeoPandas AI

GeoPandas AI is a powerful Python library that brings natural language processing capabilities to your geospatial data
analysis workflow. It allows you to interact with GeoDataFrames using natural language queries, making geospatial
analysis more accessible and intuitive. It is both suitable for Jupyter notebooks and Python scripts or packages.

## Features

- Natural language interaction with GeoDataFrames
- Support for multiple LLM providers through LiteLLM
- Built-in support for Jupyter notebooks
- Extensible and configurable.

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

figure = gdfai.chat("Plot the data")
figure = gdfai.improve("Change the title to something more selling and add a basemap")
```

### Example Usage 2

```python
import geopandas as gpd

import geopandasai as gpdai

gdf = gpd.read_file("path/to/your/geodatafile.geojson")

# Convert GeoDataFrame to GeoDataFrameAI, provide a description for the data to provide context to the LLM
gdfai = gpdai.GeoDataFrameAI(gdf, description='A GeoDataFrame containing geospatial data, the fields are..')

# Use the chat method to interact with the GeoDataFrame, syntax sugar to avoid having to go to next line and
# call gdfai.improve again.
gdfai.chat("Plot the data").improve("Change the title to something more selling and add a basemap")
```

### Example Usage 3 (Advanced parameters)

```python
import geopandasai as gpdai

gdfai = gpdai.read_file("path/to/your/geodatafile.geojson")
gdfai.set_description("A GeoDataFrame containing geospatial data, the fields are...")

a_second_df = gpdai.read_file("path/to/another/geodatafile.geojson")
a_second_df.set_description("A second GeoDataFrame containing additional geospatial data.")

value = gdfai.chat(
    "Number of clusters in the data",
    a_second_df, # Additional GeoDataFrame to use in the query, can add one or more GeoDataFrames
    provided_libraries=['scikit-learn', 'numpy'],  # Additional libraries that can be used in the generated code
    return_type=int
)

value = gdfai.improve(
    "Smaller clusters",
)

# Once happy with the result, you can save the modified GeoDataFrame
gdfai.inject(function_name="find_clusters")

# Then replace the above code with
import ai

ai.find_clusters(
    gdfai,  # The GeoDataFrame to operate on
    a_second_df,  # Additional GeoDataFrame to use in the query
)
```
)


## ⚙️ Configuration: Customizing GeoPandasAI

GeoPandasAI uses a dependency-injected configuration system for managing execution, injection, caching, and LLM-related behavior. This allows you to swap components easily for custom behavior or testing.

You can configure the lite_llm_config by using the same arguments as the ones you would provide to the `completion` function of [LiteLLM](https://docs.litellm.ai/docs/).

---

### ✨ Update the Configuration

Use update_geopandasai_config(...) to override any subset of the configuration:

```python
from geopandasai import update_geopandasai_config
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend
from geopandasai.services.description.descriptor.public import PublicDataDescriptor
from geopandasai.services.inject.injectors.print_inject import PrintCodeInjector
from geopandasai.services.code.executor import TrustedCodeExecutor, UntrustedCodeExecutor

update_geopandasai_config(
    lite_llm_config={"model": "your-llm-config"},  # dict | None
    libraries=["pandas", "geopandas", "matplotlib"],  # List[str] | None
    cache_backend=FileSystemCacheBackend(),  # ACacheBackend | None
    descriptor=PublicDataDescriptor(),  # ADescriptor | None
    return_types={int, float},  # Set[type] | None
    injector=PrintCodeInjector(),  # ACodeInjector | None
    executor=TrustedCodeExecutor(),  # ACodeExecutor | None (or UntrustedCodeExecutor())
)
```

### 🔧 Access the Current Configuration

```python
from geopandasai import get_geopandasai_config

config = get_geopandasai_config()
print(config.libraries)

```


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