import logging

logger = logging.getLogger(__name__)


class OASParser:
    @staticmethod
    def gettype(type):
        if type == "float":
            return "number"
        for i in ["string", "boolean", "integer"]:
            if type in i:
                return i
        return None

    @staticmethod
    def parse(json_data):
        d = {}
        if type(json_data) is dict:
            d["type"] = "object"
            d["properties"] = {}
            for k in json_data:
                c = OASParser.parse(json_data[k])
                if not c:
                    logger.warning(f"🚨 parsing type failed for key:{k}")
                    continue
                d["properties"][k] = c
            return d
        elif type(json_data) is list:
            if not json_data:
                return None
            d["type"] = "array"
            d["items"] = OASParser.parse(json_data[0])
            return d
        else:
            t = OASParser.gettype(type(json_data).__name__)
            if not t:
                return None
            d["type"] = t
            if d["type"] == "number":
                d["format"] = "float"
            return d
