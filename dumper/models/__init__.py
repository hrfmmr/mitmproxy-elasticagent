import pathlib
import typing as t
from functools import wraps
from enum import Enum

import yaml


YAML = str


def ensure_dest_exists(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.dest.is_file():
            assert f"dest:{self.dest} must be file"
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        return f(self, *args, **kwargs)

    return wrapper


class HTTPMethod(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class OASResponseContent:
    """
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
    """

    def __init__(
        self, dest: pathlib.Path, description: str, content: t.Dict[str, t.Any]
    ):
        self.dest = dest
        self.description = description
        self.content = content

    def build(self) -> YAML:
        oas_schema = self.parse(self.content)
        oas_json = {
            "description": self.description,
            "content": {"application/json": {"schema": oas_schema}},
        }
        return yaml.dump(oas_json)

    @ensure_dest_exists
    def write(self):
        oas_yaml = self.build()
        self.dest.write_text(oas_yaml)

    def gettype(self, type):
        if type == "float":
            return "number"
        for i in ["string", "boolean", "integer"]:
            if type in i:
                return i
        assert f"unexpected type:{type}"

    def parse(self, json_data):
        d = {}
        if type(json_data) is dict:
            d["type"] = "object"
            d["properties"] = {}
            for key in json_data:
                d["properties"][key] = self.parse(json_data[key])
            return d
        elif type(json_data) is list:
            d["type"] = "array"
            if len(json_data) != 0:
                d["items"] = self.parse(json_data[0])
            else:
                d["items"] = "object"
            return d
        else:
            d["type"] = self.gettype(type(json_data).__name__)
            if d["type"] == "number":
                d["format"] = "float"
            return d


class OASResponse:
    """
    description: Expected response to a valid request
    content:
      application/json:
        schema:
          type: object
          properties:
            id:
              type: integer
              format: int64
            name:
              type: string
    """

    def __init__(
        self,
        dest: pathlib.Path,
        status_code: int,
        resp_content: OASResponseContent,
    ):
        self.dest = dest
        self.status_code = status_code
        self.resp_content = resp_content

    def build_ref_json(self) -> t.Dict[str, t.Any]:
        return {self.status_code: {"$ref": f"{self.status_code}/_index.yml"}}

    def write(self):
        self.resp_content.write()


class OASResponseList:
    """
    '200':
      $ref: '200/_index.yml'
    """

    def __init__(self, dest: pathlib.Path, responses: t.List[OASResponse]):
        self.dest = dest
        self.responses = responses

    def build(self) -> YAML:
        oas_json = {}
        for resp in self.responses:
            oas_json.update(resp.build_ref_json())
        return yaml.dump(oas_json)

    def write(self):
        for resp in self.responses:
            resp.write()
        oas_yaml = self.build()
        self.dest.write_text(oas_yaml)


class OASPathMethod:
    """
    summary: Info for a specific pet
    operationId: showPetById
    tags:
      - pets
    responses:
      $ref: "responses.yml"
    """

    def __init__(
        self,
        dest: pathlib.Path,
        method: HTTPMethod,
        summary,
        operation_id,
        resp_list: OASResponseList,
    ):
        self.summary = summary
        self.operation_id = operation_id
        self.resp_list = resp_list

    def build_ref_json(self):
        return {self.method.value: {"$ref": f"{self.method.value}/_index.yml"}}

    def build(self) -> YAML:
        oas_json = {
            "summary": self.summary,
            "operationId": self.operation_id,
            "responses": {"$ref": "responses/_index.yml"},
        }
        return yaml.dump(oas_json)

    def write(self):
        self.resp_list.write()
        oas_yaml = self.build()
        self.dest.write_text(oas_yaml)


class OASPathMethodList:
    """
    get:
      $ref: 'get/_index.yml'
    post:
      $ref: 'post/_index.yml'
    """

    def __init__(self, dest: pathlib.Path, methods: t.List[OASPathMethod]):
        self.dest = dest
        self.methods = methods

    def build(self) -> YAML:
        oas_json = {}
        for method in self.methods:
            oas_json.update(method.build_ref_json())
        return yaml.dump(oas_json)

    def write(self):
        for method in self.methods:
            method.write()
        oas_yaml = self.build()
        self.dest.write_text(oas_yaml)


class OASEndpoint:
    """
    /pets:
      $ref: "paths/pets/_index.yml"
    """

    def __init__(
        self, dest: pathlib.Path, endpoint: str, method_list: OASPathMethodList
    ):
        self.dest = dest
        self.endpoint = endpoint
        self.endpoint_dir = endpoint.replace("/", "_")[1:]

    def build_ref_json(self):
        return {
            self.endpoint: {"$ref": f"paths/{self.endpoint_dir}/_index.yml"}
        }

    def write(self):
        self.method_list.write()


class OASEndpointList:

    """
    paths:
      /pets:
        $ref: "paths/pets/_index.yml"
    """

    def __init__(self, endpoint_list: t.List[OASEndpoint]):
        self.endpoint_list = endpoint_list

    def build(self) -> YAML:
        oas_json = {}
        for endpoint in self.endpoint_list:
            oas_json.update(endpoint.build_ref_json())
        return yaml.dump(oas_json)

    def write(self):
        for endpoint in self.endpoint_list:
            endpoint.write()
        oas_yaml = self.build()
        # TODO: あー、pathsも、本来paths: $ref: "paths/_indexyml"になってる必要あるな
        self.dest.write_text(oas_yaml)
