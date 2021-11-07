import pathlib


def endpoint_root_dir() -> pathlib.Path:
    return pathlib.Path("paths")


def endpoint_dir(endpoint_path: str) -> pathlib.Path:
    return endpoint_root_dir() / to_endpoint_dir(endpoint_path)


def to_endpoint_dir(endpoint_path: str) -> str:
    return endpoint_path.replace("/", "_")[1:]


def to_endpoint_path(dir_name: str) -> str:
    return "/" + dir_name.replace("_", "/")


def response_description(status_code: int) -> str:
    if status_code >= 200 and status_code < 300:
        return "Expected response to a valid request"
    else:
        return "Error response"
