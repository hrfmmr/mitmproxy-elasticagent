class OASParser:
    @staticmethod
    def gettype(type):
        if type == "float":
            return "number"
        for i in ["string", "boolean", "integer"]:
            if type in i:
                return i
        assert f"unexpected type:{type}"

    @staticmethod
    def parse(json_data):
        d = {}
        if type(json_data) is dict:
            d["type"] = "object"
            d["properties"] = {}
            for key in json_data:
                d["properties"][key] = OASParser.parse(json_data[key])
            return d
        elif type(json_data) is list:
            d["type"] = "array"
            if len(json_data) != 0:
                d["items"] = OASParser.parse(json_data[0])
            else:
                d["items"] = "object"
            return d
        else:
            d["type"] = OASParser.gettype(type(json_data).__name__)
            if d["type"] == "number":
                d["format"] = "float"
            return d
