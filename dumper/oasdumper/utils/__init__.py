import re
import pathlib


def endpoint_root_dir() -> pathlib.Path:
    return pathlib.Path("paths")


def endpoint_dir(endpoint_path: str) -> pathlib.Path:
    path = parameterized_endpoint_path(endpoint_path)
    return endpoint_root_dir() / to_endpoint_dir(path)


def to_endpoint_dir(endpoint_path: str) -> str:
    return endpoint_path.replace("/", "_")[1:]


def to_endpoint_path(dir_name: str) -> str:
    p = r"{[\w]+}"
    path_params = re.findall(p, dir_name)
    if path_params:
        mask = "XXX"
        masked = re.sub(p, mask, dir_name)
        param_it = iter((range(len(path_params))))
        return "/" + "/".join(
            [
                s if s != mask else path_params[next(param_it)]
                for s in masked.split("_")
            ]
        )
    else:
        return "/" + dir_name.replace("_", "/")


def parameterized_endpoint_path(endpoint_path: str) -> str:
    """
    eg.
        in: /v1/posts/100/comments/2
        out: /v1/posts/{post_id}/comments/{comment_id}
    """
    components = endpoint_path.split("/")
    for i, c in enumerate(components):
        if c.isdigit():
            res = components[i - 1]
            res_id_descriptor = "{" + f"{res[:-1]}_id" + "}"
            components[i] = res_id_descriptor
    return "/".join(components)


def response_description(status_code: int) -> str:
    if status_code >= 200 and status_code < 300:
        return "Expected response to a valid request"
    else:
        return "Error response"
