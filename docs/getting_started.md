# 🧪 Getting Started with GeoPandas-AI

Welcome to **GeoPandas-AI** — a Python library that transforms your `GeoDataFrame` into a conversational, intelligent assistant powered by large language models (LLMs). This guide walks you through installation, basic usage, stateful chatting, caching, and advanced configuration.

---

## 📦 Installation

GeoPandas-AI requires **Python 3.8+**. Install via pip:

```bash
pip install geopandas-ai
````

This will pull in dependencies including GeoPandas and LiteLLM.

---

## 📂 Supported Data Formats

GeoPandas-AI works with any file `geopandas.read_file()` supports:

* GeoJSON
* Shapefile
* GeoPackage
* Or wrap an existing `GeoDataFrame`

---

## 🚀 First Steps

### 1. Load spatial data and ask a question

```python
import geopandasai as gpdai

gdfai = gpdai.read_file("data/cities.geojson")
gdfai.chat("Plot the cities by population")
```

### 2. Refine the output in plain English

```python
gdfai.improve("Add a basemap and set the title to 'City Population Map'")
```

### 3. Wrap an existing `GeoDataFrame`

```python
import geopandas as gpd
from geopandasai import GeoDataFrameAI

gdf = gpd.read_file("parks.geojson")
gdfai = GeoDataFrameAI(
    gdf,
    description="Public parks with name, area, and geometry"
)

gdfai.chat("Show the largest five parks by area")
```

---

## 🔁 Stateful Chatting

GeoPandas-AI preserves context across turns:

```python
gdfai.chat("Cluster the parks by area using KMeans")
gdfai.improve("Use different colors for each cluster and display centroids")
```

You can combine multiple datasets in one conversation:

```python
schools = gpdai.read_file("schools.geojson")
zones   = gpdai.read_file("zones.geojson")

schools.set_description("Public school locations")
zones.set_description("City zoning polygons")

schools.chat(
  "Count how many schools fall into each zone",
  zones,
  return_type=DataFrame
)
```

---

## 🧠 Caching & Backend Configuration

GeoPandas-AI uses a **dependency-injection** config system (via `dependency_injector`) to manage:

* **Cache backend**
* **LLM settings**
* **Code executor**
* **Code injector**
* **Data descriptor**
* **Allowed return types**

### Why caching?

All `.chat()` and `.improve()` calls are memoized. Repeating the same prompt **reuses** cached results—no new LLM call—saving tokens and time.

### Default cache backend

By default, GeoPandas-AI uses a filesystem cache:

```python
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend

# Default writes to `.gpd_cache/` in your working directory
```

### Customize configuration

Use `update_geopandasai_config()` to override defaults:

```python
from geopandasai import update_geopandasai_config
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend
from geopandasai.services.inject.injectors.print_inject import PrintCodeInjector
from geopandasai.services.code.executor import TrustedCodeExecutor

update_geopandasai_config(
  cache_backend=FileSystemCacheBackend(cache_dir=".gpd_cache"),
  executor=TrustedCodeExecutor(),
  injector=PrintCodeInjector(),
  libraries=["pandas","matplotlib.pyplot","folium","geopandas","contextily"],
)
```

### Forcing a fresh LLM call

To clear cache and memory, use:

```python
gdfai.reset()
```

---

## 💥 Advanced Usage: Injection & Modularity

### Inspect generated code

```python
print(gdfai.code)    # View last generated Python code
gdfai.inspect()      # Print prompt, code, and result history
```

### Inject code into your project

Persist or reuse AI-generated functions:

```python
gdfai.inject("my_custom_function")
# This writes the function into ai.py (or your chosen module)
```

Then call it as a normal function:

```python
import ai
df = ai.my_custom_function(gdf1, gdf2)
```

---

## 📚 Next Steps

* **Examples:** see `examples/` in the GitHub repo
* **API Reference:** `api.md` (with `mkdocstrings`)
* **Read the Paper:** [arXiv:2506.11781](https://arxiv.org/abs/2506.11781)

---

## 🆘 Troubleshooting

* **No output?** Ensure you’re in a Jupyter notebook or assign `.chat()` to a variable.
* **LLM errors/timeouts?** Check your LiteLLM backend configuration.
* **Stale prompts?** Call `gdfai.reset()` to clear conversation memory.

> *GeoPandas-AI makes geospatial analysis conversational, intelligent, and reproducible.*

