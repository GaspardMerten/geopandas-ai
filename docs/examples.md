# 📘 Examples

This page provides end-to-end example workflows showcasing GeoPandas-AI in action, including how to extend it with **custom backends** (cache, injector, descriptor, executor).

---

## 1. Interactive Visualization & Refinement

```python
import geopandasai as gpdai

# Load a GeoJSON of world capitals
gdfai = gpdai.read_file("data/world_capitals.geojson")

# 1.1 Plot capitals sized by population
fig1 = gdfai.chat("Create a scatter plot of world capitals, sizing points by population")
fig1

# 1.2 Improve: add title, legend, and basemap
fig2 = gdfai.improve(
    "Add a descriptive title, show a legend for population size, and overlay a contextily basemap"
)
fig2
````

---

## 2. Filtering & Tabular Output

```python
from geopandasai import GeoDataFrameAI
import geopandas as gpd

# Load neighborhoods dataset
gdf = gpd.read_file("data/neighborhoods.geojson")
gdfai = GeoDataFrameAI(gdf, description="Neighborhood polygons with demographics")

# 2.1 List neighborhoods with population density > 5000 people/km²
high_density = gdfai.chat(
    "Return a GeoDataFrame of neighborhoods with density over 5000 people per square kilometer",
    return_type=type(gdf)  # returns a GeoDataFrame
)
high_density.head()
```

---

## 3. Multi-Dataset Spatial Join

```python
# Load two datasets
schools = gpdai.read_file("data/schools.geojson")
zones   = gpdai.read_file("data/zoning.geojson")

# Describe each
schools.set_description("Point locations of public schools")
zones.set_description("Polygon boundaries of administrative zones")

# 3.1 Count schools per zone
count_df = schools.chat(
    "For each zone, count how many schools fall within it and return a DataFrame with zone_id and count",
    zones,
    return_type=type(zones)  # DataFrame or GeoDataFrame
)
count_df.head()
```

---

## 4. Clustering & Map Styling

```python
# Cluster city crime incidents
incidents = gpdai.read_file("data/crime_incidents.geojson")
incidents.set_description("Crime incident points with latitude, longitude, and type")

# 4.1 Cluster incidents into 4 clusters using KMeans
clusters = incidents.chat(
    "Cluster the crime incidents into 4 spatial clusters using scikit-learn",
    provided_libraries=["scikit-learn"],
    return_type=int
)
# clusters is a pandas Series of cluster labels

# 4.2 Visualize clusters with distinct colors
incidents.improve(
    "Plot the incident points colored by cluster label and add a legend"
)
```

---

## 5. Caching & Reuse

```python
# Running the same prompt twice uses cache
parks = gpdai.read_file("data/parks.geojson")
parks.set_description("City park polygons with area")

# First run invokes LLM
parks.chat("Plot parks with area > 100 hectares")

# Second run reuses cached result (no LLM call)
parks.chat("Plot parks with area > 100 hectares")
```

---

## 6. Code Inspection & Injection

```python
# Inspect last generated code
print(parks.code)

# Inject the function into ai.py for reuse
parks.inject("plot_large_parks")

# In another script or cell:
import ai
ai.plot_large_parks(parks)
```

---

## 7. Custom Configuration

```python
from geopandasai import update_geopandasai_config
from geopandasai.external.cache.backend.file_system import FileSystemCacheBackend
from geopandasai.services.inject.injectors.print_inject import PrintCodeInjector
from geopandasai.services.code.executor import TrustedCodeExecutor

# Redirect cache to custom folder and use print injector
update_geopandasai_config(
    cache_backend=FileSystemCacheBackend(cache_dir="custom_cache"),
    injector=PrintCodeInjector(),
    executor=TrustedCodeExecutor()
)
```

---

## 8. Extending GeoPandas-AI with Custom Backends

### 8.1 Custom Code Injector

Subclass `ACodeInjector` to define how code is inserted into your project. For example, the built-in `PythonCodeInjector` searches your source file for a pattern and replaces it:

```python
import inspect, re
from typing import Callable, Optional
from geopandasai.services.inject.injectors.base import ACodeInjector

class PythonCodeInjector(ACodeInjector):
    def inject(
        self,
        pattern: re.Pattern,
        function_call_builder: Callable[[Optional[re.Match]], str],
        import_statement: str,
    ):
        # Locate the calling file
        frame = inspect.currentframe()
        filename = frame.f_back.f_back.f_back.f_code.co_filename
        with open(filename, "r") as f:
            code = f.read()
        # Find the first match
        match = pattern.search(code)
        if not match:
            raise ValueError("Pattern not found in code.")
        # Add import if missing
        if import_statement not in code:
            code = f"{import_statement}\n{code}"
        # Replace the matched call with your generated function call
        new_code = code.replace(match.group(0), function_call_builder(match))
        with open(filename, "w") as f:
            f.write(new_code)
```

Configure GeoPandas-AI to use it:

```python
from geopandasai import update_geopandasai_config
from mymodule.injectors import PythonCodeInjector

update_geopandasai_config(injector=PythonCodeInjector())
```

---

### 8.2 Custom Data Descriptor

Subclass `ADescriptor` to control the data summary sent to the LLM. Example: `PublicDataDescriptor` includes schema, stats, and sample rows:

```python
import geopandas as gpd
import pandas as pd
from geopandasai.services.description.descriptor.base import ADescriptor
from geopandasai.shared.return_type import type_to_literal

class PublicDataDescriptor(ADescriptor):
    def __init__(self, sample_rows: int = 20):
        super().__init__()
        self.sample_rows = sample_rows

    def describe(self, instance) -> str:
        desc = f"Type: {type_to_literal(type(instance))}\n"
        if isinstance(instance, gpd.GeoDataFrame):
            desc += f"CRS: {instance.crs}\n"
            desc += f"Geometry types: {', '.join(instance.geometry.geom_type.unique())}\n"
        desc += f"Shape: {instance.shape}\n"
        desc += instance.describe().to_string() + "\n"
        sample = instance.sample(min(len(instance), self.sample_rows), random_state=42)
        desc += "Sample rows:\n" + sample.to_string(index=False)
        return desc
```

Activate it:

```python
from geopandasai import update_geopandasai_config
from mymodule.descriptors import PublicDataDescriptor

update_geopandasai_config(descriptor=PublicDataDescriptor(sample_rows=10))
```

---

### 8.3 Custom Code Executor

Subclass `TrustedCodeExecutor` to add safety checks or confirmations. Example: `UntrustedCodeExecutor` shows code with syntax highlighting and asks for user approval before executing:

```python
import re
from colorama import Fore, Style
from geopandasai.services.code.executor.trusted import TrustedCodeExecutor

def highlight(code: str) -> str:
    # Simple color highlighting for Python keywords and strings
    code = re.sub(r"\b(def|return|if|else|import|from)\b", 
                  lambda m: Fore.BLUE + m.group(0) + Style.RESET_ALL, code)
    code = re.sub(r"(\".*?\"|\'.*?\')", 
                  lambda m: Fore.GREEN + m.group(0) + Style.RESET_ALL, code)
    return code

class UntrustedCodeExecutor(TrustedCodeExecutor):
    def execute(self, code: str, return_type, *dfs):
        print(highlight(code))
        confirm = input("Execute this code? (y/N): ").lower() == "y"
        if not confirm:
            raise RuntimeError("Execution aborted by user.")
        return super().execute(code, return_type, *dfs)
```

Use it:

```python
from geopandasai import update_geopandasai_config
from mymodule.executors import UntrustedCodeExecutor

update_geopandasai_config(executor=UntrustedCodeExecutor())
```

---

> ❗ **Tip:** After customizing any backend, call `.reset()` on your `GeoDataFrameAI` instance to clear prior state and ensure new settings take effect.

Happy hacking!

