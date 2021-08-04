from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import json
import time

import requests
from requests import Response
from requests.auth import AuthBase

from juggle_challenge import utils


def decode_content(content: bytes) -> Tuple[str, Any]:
    try:
        content = json.loads(content)
        return "json", content
    except json.JSONDecodeError:
        pass

    try:
        content = content.decode()
        return "text", content
    except UnicodeDecodeError:
        pass

    return "binary", content


def json_fmt(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def log_request(method, url, data) -> None:
    print(f"{method} {url}")
    if method.lower() not in {"get", "head"}:
        print(json_fmt(data))


def log_response(response: requests.Response, dt_s: float) -> None:
    print(f"{response.status_code} {response.reason}  dt_s={dt_s:.3}")

    if 300 <= response.status_code < 400:
        print(f"Location: {response.headers['location']}\n")
        return

    content_type, content = decode_content(response.content)
    if content_type == "json":
        print(json_fmt(content))
    elif content_type == "text":
        print(content[:4096])
    elif content_type == "binary":
        print(repr(content)[:4096])
    print()


class RestApiResponseException(Exception):
    pass


@dataclass
class BaseBearerAuth(AuthBase):
    def _get_api_token(self):
        raise NotImplementedError()

    def __call__(self, r: requests.Request) -> requests.Request:
        token = self._get_api_token()
        r.headers["authorization"] = f"Bearer {token}"
        return r


@dataclass
class BearerAuth(BaseBearerAuth):
    token: str

    def _get_api_token(self):
        return self.token


@dataclass
class Request:
    method: str
    path: str
    headers: Optional[Dict] = None
    data: Optional[Dict] = None
    files: Optional[Dict] = None


@dataclass
class Client:
    auth: Optional[AuthBase] = None
    base_url: Optional[str] = None
    default_headers: Optional[dict] = None
    create_response: Optional[Callable] = utils.create_response
    exception_raise_enabled: Optional[bool] = True

    def __call__(self, path: str) -> "Endpoint":
        return Endpoint(client=self, path=path)

    def _send(self, request: Request) -> Response:
        url = f"{self.base_url}{request.path}"
        log_request(request.method, url=request.path, data=request.data)

        if self.base_url is None:
            return self.create_response(status_code=200)

        t0 = time.perf_counter()
        if request.files is None:
            extra = dict(json=request.data)
        else:
            extra = dict(data=request.data, files=request.files)
        headers = dict()
        headers.update(request.headers or dict())
        headers.update(self.default_headers or dict())
        response = requests.request(
            allow_redirects=False,
            auth=self.auth,
            method=request.method,
            url=url,
            headers=headers,
            **extra,
        )
        t = time.perf_counter()

        log_response(response, dt_s=t - t0)
        if self.exception_raise_enabled and (not 200 <= response.status_code < 300):
            raise RestApiResponseException(f"{response.text}")
        return response

    def send(
        self,
        method: str,
        path: str,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
    ) -> Response:
        return self._send(
            Request(method=method, path=path, headers=headers, data=data, files=files)
        )


@dataclass
class Endpoint:
    client: Client
    path: str

    def get(self) -> Any:
        return self.client.send(method="GET", path=self.path)

    def patch(self, **data) -> Any:
        return self.client.send(method="PATCH", path=self.path, data=data)

    def post(self, **data) -> Any:
        return self.client.send(method="POST", path=self.path, data=data)

    def put(self, **data) -> Any:
        return self.client.send(method="PUT", path=self.path, data=data)

    def delete(self, **data) -> Any:
        return self.client.send(method="DELETE", path=self.path, data=data)

    def post_files(self, files: dict, **data) -> Any:
        return self.client.send(method="POST", path=self.path, files=files, data=data)
