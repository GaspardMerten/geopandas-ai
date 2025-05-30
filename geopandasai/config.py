import json
import os
from dataclasses import dataclass, field, replace
from typing import List, Optional, Type, Set

from dependency_injector import containers, providers
from folium import folium
from geopandas import GeoDataFrame
from matplotlib.figure import Figure
from pandas import DataFrame
from typing_extensions import deprecated

from .external.cache.backend.base import ACacheBackend
from .external.cache.backend.file_system import FileSystemCacheBackend
from .services.code.executor import TrustedCodeExecutor, ACodeExecutor
from .services.description.descriptor.base import ADescriptor
from .services.description.descriptor.public import PublicDataDescriptor
from .services.inject.injectors import ACodeInjector
from .services.inject.injectors.print_inject import PrintCodeInjector


@dataclass(frozen=True, eq=True)
class GeoPandasAIConfig:
    lite_llm_config: Optional[dict] = field(
        default_factory=lambda: _load_default_lite_llm_config()
    )
    libraries: List[str] = field(
        default_factory=lambda: [
            "pandas",
            "matplotlib.pyplot",
            "folium",
            "geopandas",
            "contextily",
        ]
    )

    cache_backend: ACacheBackend = FileSystemCacheBackend()

    descriptor: ADescriptor = PublicDataDescriptor()

    injector: ACodeInjector = PrintCodeInjector()

    executor: ACodeExecutor = TrustedCodeExecutor()

    return_types: Set[Type] = field(
        default_factory=lambda: {
            int,
            float,
            str,
            bool,
            list,
            dict,
            GeoDataFrame,
            DataFrame,
            folium.Map,
            Figure,
        }
    )


def _load_default_lite_llm_config() -> Optional[dict]:
    if "LITELLM_CONFIG" in os.environ:
        return json.loads(os.environ["LITELLM_CONFIG"])
    return None


class GeoPandasAIContainer(containers.DeclarativeContainer):
    config = providers.Singleton(GeoPandasAIConfig)


# Global container instance (can be scoped if needed)
container = GeoPandasAIContainer()


def get_geopandasai_config() -> GeoPandasAIConfig:
    return container.config()


@deprecated(
    "This function is deprecated and will be removed in future versions. Use `update_geopandas_ai_config` instead.",
)
def set_active_lite_llm_config(lite_llm_config: dict) -> None:
    """Set the active lite LLM configuration."""
    current_config = container.config()
    updated_config = replace(current_config, lite_llm_config=lite_llm_config)
    container.config.override(updated_config)


def update_geopandasai_config(
    lite_llm_config: Optional[dict] = None,
    libraries: Optional[List[str]] = None,
    cache_backend: Optional[ACacheBackend] = None,
    descriptor: Optional[ADescriptor] = None,
    return_types: Optional[Set[Type]] = None,
    injector: Optional[ACodeInjector] = None,
    executor: Optional[ACodeExecutor] = None,
) -> None:
    """Update the GeoPandasAI configuration.

    This function allows you to update the configuration of GeoPandasAI, including
    the lite LLM configuration, libraries, cache backend, descriptor, return types,
    and code injector. If a parameter is not provided, the current value will be retained.
    :param lite_llm_config: The configuration for the lite LLM, if any.
    :param libraries: A list of libraries to be used in the GeoPandasAI environment.
    :param cache_backend: The cache backend to be used.
    :param descriptor: The data descriptor to be used.
    :param return_types: A set of types that can be returned by the AI.
    :param injector: The code injector to be used.
    :param executor: The code executor to be used.
    """

    current_config = container.config()
    updated_config = replace(
        current_config,
        lite_llm_config=(
            lite_llm_config
            if lite_llm_config is not None
            else current_config.lite_llm_config
        ),
        libraries=libraries if libraries is not None else current_config.libraries,
        cache_backend=(
            cache_backend if cache_backend is not None else current_config.cache_backend
        ),
        descriptor=(
            descriptor if descriptor is not None else current_config.descriptor
        ),
        return_types=(
            return_types if return_types is not None else current_config.return_types
        ),
        injector=(injector if injector is not None else current_config.injector),
        executor=(executor if executor is not None else current_config.executor),
    )
    container.config.override(updated_config)
