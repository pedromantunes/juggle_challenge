import datetime
import time as stdlib_time
import requests
from io import BytesIO
from typing import Generator, List, Any, Optional
import simplejson as json

from django.conf import settings


def time() -> float:
    return stdlib_time.time()


def now(tz=None) -> datetime.datetime:
    t = time()
    return datetime.datetime.fromtimestamp(t, tz)


def now_us() -> int:
    return int(time() * 1_000_000)


def now_with_tz() -> datetime.datetime:
    return now(tz=datetime.timezone.utc)


def build_absolute_url(path: str) -> str:
    base_url = getattr(settings, "SITE_BASE_URL", None)
    base_url = base_url if base_url else "http://127.0.0.1:8000"
    return f"{base_url}{path}"


def filter_items(
    items_id: Optional[List[str]], item_id_name: str, items: List[Any]
) -> Generator[Any, None, None]:
    if not items_id:
        return []

    for item_id in items_id:
        for item in items:
            if type(item) == dict:
                if item_id == item.get(item_id_name, None):
                    yield item
            else:
                if item_id == getattr(item, item_id_name):
                    yield item


def create_response(status_code: int, body: Optional = "mocked") -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.encoding = "utf8"
    reason = json.dumps(body)
    response.raw = BytesIO(reason.encode(response.encoding))
    if status_code == HTTPStatus.BAD_REQUEST:
        response.reason = reason
    return response
