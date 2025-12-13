from src.config import settings
print(f"Project Root: {settings.project_root}")
print(f"Is Path: {hasattr(settings.project_root, 'joinpath')}")
