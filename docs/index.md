# GeoPandas-AI

<img src="https://raw.githubusercontent.com/GaspardMerten/geopandas-ai/main/docs/assets/icon.avif" height="100" alt="GeoPandas-AI Logo" style="max-width: 250px">

**GeoPandas-AI** is an open-source Python library that enhances geospatial data analysis by turning the `GeoDataFrame` into a conversational, intelligent assistant. It seamlessly integrates large language models (LLMs) into the geospatial workflow, enabling natural language interaction, iterative refinement, caching, and code generation directly within your Python environment.

[![PyPI version](https://badge.fury.io/py/geopandas-ai.svg)](https://pypi.org/project/geopandas-ai/)  
[![arXiv](https://img.shields.io/badge/arXiv-2506.11781-b31b1b.svg)](https://arxiv.org/abs/2506.11781)  
[View on GitHub →](https://github.com/GaspardMerten/geopandas-ai)

---

## 🌍 Motivation

Geospatial data is key to solving complex problems in urban planning, environmental science, and infrastructure development. But tools like [GeoPandas](https://geopandas.org) require familiarity with both GIS concepts and Python-based workflows.

**GeoPandas-AI** lowers this barrier by:

- Embedding conversational AI directly into `GeoDataFrame`  
- Enabling plain-language queries and refinements  
- Supporting reproducible, scriptable workflows with AI-assisted code  
- Caching results to avoid redundant LLM calls  

This bridges human interaction with geospatial analysis in a seamless and stateful way.

---

## 🧠 What’s New?

Based on the [arXiv preprint](https://arxiv.org/abs/2506.11781), **GeoPandas-AI** introduces:

- ✅ A stateful, LLM-augmented `GeoDataFrameAI` class  
- ✅ `.chat()` and `.improve()` methods for language-based querying and iteration  
- ✅ Built-in caching: repeated prompts reuse cached results (no extra LLM calls)  
- ✅ Full compatibility with existing `GeoDataFrame` workflows  
- ✅ Modular backends for execution, injection, caching, and LLM calls  
- ✅ A vision of conversational programming for geospatial developers  

> Read the paper: [_GeoPandas-AI: A Smart Class Bringing LLM as Stateful AI Code Assistant_](https://arxiv.org/abs/2506.11781)

---

## ⚙️ Installation

```bash
pip install geopandas-ai
````

Python 3.8+ required.

---

## 🚀 Quick Start

### Example 1: Read and visualize spatial data interactively

```python
import geopandasai as gpdai

gdfai = gpdai.read_file("cities.geojson")
gdfai.chat("Plot the cities by population")
gdfai.improve("Add a title and a basemap")
```

---

### Example 2: Wrap an existing GeoDataFrame

```python
import geopandas as gpd
from geopandasai import GeoDataFrameAI

gdf = gpd.read_file("parks.geojson")
gdfai = GeoDataFrameAI(
    gdf,
    description="City parks with name, area, and geometry"
)

gdfai.chat("Show the largest 5 parks")
```

---

### Example 3: Work with multiple dataframes

```python
a = gpdai.read_file("zones.geojson")
b = gpdai.read_file("reference.geojson")

a.set_description("Zoning polygons for city planning")
b.set_description("Reference dataset with official labels")

a.chat(
    "Cluster the zones into 3 groups based on geometry size",
    b,
    provided_libraries=["scikit-learn", "numpy"],
    return_type=int
)
```

---

## 🔧 Configuration & Caching

GeoPandas-AI uses a flexible dependency-injection architecture (via `dependency_injector`) to manage:

* **LiteLLM** settings
* **Cache backend** (memoizes `.chat()` and `.improve()` calls)
* **Code executor** (trusted or sandboxed)
* **Code injector**
* **Data descriptor**
* **Allowed return types**

### Built-in caching

By default, responses and generated code are cached on disk:

```python
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend

# Default writes to `.gpd_cache/`
```

Any repeated prompt or improvement will reuse cached results, saving tokens and accelerating workflows.

### Customizing configuration

Override defaults with `update_geopandasai_config()`:

```python
from geopandasai import update_geopandasai_config
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend
from geopandasai.services.inject.injectors.print_inject import PrintCodeInjector
from geopandasai.services.code.executor import TrustedCodeExecutor

update_geopandasai_config(
    cache_backend=FileSystemCacheBackend(cache_dir=".gpd_cache"),
    executor=TrustedCodeExecutor(),
    injector=PrintCodeInjector(),
    libraries=[
      "pandas",
      "matplotlib.pyplot",
      "folium",
      "geopandas",
      "contextily",
    ],
)
```

### Forcing fresh LLM calls

To clear all memory and cache for a fresh start:

```python
gdfai.reset()
```

---

## 📚 Learn More

* [📦 PyPI Package](https://pypi.org/project/geopandas-ai/)
* [📖 arXiv Preprint](https://arxiv.org/abs/2506.11781)
* [📘 Example Notebooks](https://github.com/GaspardMerten/geopandas-ai/tree/main/examples)
* [🧠 LiteLLM Docs](https://docs.litellm.ai/)
* [🛠 GitHub Repository](https://github.com/GaspardMerten/geopandas-ai)

---

## 📄 Citation

If you use GeoPandas-AI in academic work, please cite:

```
@misc{merten2025geopandasaismartclassbringing,
  title={GeoPandas-AI: A Smart Class Bringing LLM as Stateful AI Code Assistant}, 
  author={Gaspard Merten and Gilles Dejaegere and Mahmoud Sakr},
  year={2025},
  eprint={2506.11781},
  archivePrefix={arXiv},
  primaryClass={cs.HC},
  url={https://arxiv.org/abs/2506.11781}, 
}
```

---

## 🪪 License

MIT License – see [LICENSE](https://github.com/GaspardMerten/geopandas-ai/blob/main/LICENSE.MD) for details.

> *GeoPandas-AI: Making geospatial analysis conversational, intelligent, and reproducible.*
