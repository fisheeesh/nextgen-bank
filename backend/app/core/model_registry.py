import importlib
import os
import pathlib

from .logging import get_logger

logger = get_logger()


def get_app_package() -> str:
    return __package__.removesuffix(".core") # type: ignore


def discover_models() -> list[str]:
    models_modules = []
    root_path = pathlib.Path(__file__).parent.parent
    app_package = get_app_package()

    logger.debug(f"Searching for models in the root path: {root_path}")

    # ? root is the current directory, _ is sub directory, and files is the list of files in the current directory
    for root, _, files in os.walk(root_path):
        if any(
            excluded in root for excluded in ["venv", "__pycache__", ".pytest_cache"]
        ):
            continue

        if "models.py" in files:
            rel_path = os.path.relpath(root, root_path)
            module_path = rel_path.replace(os.path.sep, ".")

            if module_path == ".":
                full_module_path = f"{app_package}.models"
            else:
                full_module_path = f"{app_package}.{module_path}.models"

            logger.debug(f"Discovered models file in: {full_module_path}")

            models_modules.append(full_module_path)
    return models_modules


def load_models() -> None:
    modules = discover_models()
    for module_path in modules:
        try:
            importlib.import_module(module_path)
            logger.debug(f"Imported module {module_path}")
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
