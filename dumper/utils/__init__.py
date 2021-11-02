import pathlib


def endpoint_dir(endpoint_path: str) -> pathlib.Path:
    root = endpoint_path.replace("/", "_")[1:]
    return pathlib.Path("paths") / root


def response_description(status_code: int) -> str:
    if status_code >= 200 and status_code < 300:
        return "Expected response to a valid request"
    else:
        return "Error response"
