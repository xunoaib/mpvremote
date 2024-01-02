from .metadata import ApiException
from .web import create_app

try:
    app = create_app()
except ApiException as exc:
    print(exc)
