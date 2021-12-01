import re
import pathlib
import typing as t

from oasdumper.models import HTTPMethod, SchemaType

DELIMITER = "-"
RES_DELIMITER = "_"


def endpoint_root_dir() -> pathlib.Path:
    return pathlib.Path("paths")


def schema_root_dir() -> pathlib.Path:
    return pathlib.Path("components/schemas")


def endpoint_dir(endpoint_path: str) -> pathlib.Path:
    path = parameterized_endpoint_path(endpoint_path)
    return endpoint_root_dir() / to_endpoint_dir(path)


def endpoint_schema_dir(endpoint_path: str) -> pathlib.Path:
    path = parameterized_endpoint_path(endpoint_path)
    return schema_root_dir() / to_endpoint_dir(path)


def to_endpoint_dir(endpoint_path: str) -> str:
    return endpoint_path.replace("/", DELIMITER)[1:]


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
                for s in masked.split(DELIMITER)
            ]
        )
    else:
        return "/" + dir_name.replace(DELIMITER, "/")


def response_description(status_code: int) -> str:
    if status_code >= 200 and status_code < 300:
        return "Expected response to a valid request"
    else:
        return "Error response"


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


def is_parameterized(endpoint_path: str) -> bool:
    rex_path_param = re.compile(r"^{(?P<res_id>.*_?id)}$")
    for c in endpoint_path.split("/"):
        if rex_path_param.match(c):
            return True
    return False


def build_path_params(endpoint_path: str) -> t.Dict[str, t.Any]:
    """
    eg.
        in: /v1/posts/100/comments/2
        out: {'post_id': 100, 'comment_id': 2}
    """
    path_params = {}
    parameterized_path = parameterized_endpoint_path(endpoint_path)
    rex_path_param = re.compile(r"^{(?P<res_id>.*_?id)}$")
    orig_components = endpoint_path.split("/")
    for i, c in enumerate(parameterized_path.split("/")):
        result = rex_path_param.match(c)
        if result:
            path_params[result.group("res_id")] = int(orig_components[i])
    return path_params


def build_operation_id(method: HTTPMethod, endpoint_path: str) -> str:
    """
    eg.
        in: ('get', '/v1/posts/1/comments')
        out: 'getPostComments'
    """
    rex = re.compile(r"^/v[\d]+/(?P<path>.+)")
    result = re.match(rex, endpoint_path)
    path_without_version = result.group("path")
    if is_parameterized(endpoint_path):
        rex_path_param = re.compile(r"{(?P<res_id>.*_?id)}")
        path_params = rex_path_param.findall(endpoint_path)
        operation_res = [
            s.capitalize()[:-1]
            if [k for k in path_params if s[:-1] in k]
            else s.capitalize()
            for s in path_without_version.split("/")
            if not rex_path_param.match(s)
        ]
    else:
        path_params = build_path_params(endpoint_path)
        operation_res = [
            s.capitalize()[:-1]
            if [k for k in path_params if s[:-1] in k]
            else s.capitalize()
            for s in path_without_version.split("/")
            if not s.isdigit()
        ]
    operation_id = method.value + "".join(operation_res)

    if RES_DELIMITER not in operation_id:
        return operation_id
    components = operation_id.split(RES_DELIMITER)
    return components[0] + "".join([x.capitalize() for x in components[1:]])


def build_schema_identifier(
    method: HTTPMethod, endpoint_path: str, schema_type: SchemaType
) -> str:
    opid = build_operation_id(method, endpoint_path)
    return opid[0].upper() + opid[1:] + schema_type.value
