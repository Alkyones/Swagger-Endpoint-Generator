import argparse
import json
import yaml
import pyclip

TYPE_MAPPING = {
    'str': 'string',
    'int': 'integer',
    'float': 'number',
    'list': 'array',
    'dict': 'object',
    'bool': 'boolean',
    'NoneType': 'null',
}

def create_swagger_definition(schema_name, schema_type, schema_data):
    swagger_definition = {
        "type": TYPE_MAPPING.get(schema_type, schema_type),
    }

    if schema_type == "object":
        properties = {}
        for key, value in schema_data.items():
            if isinstance(value, dict):
                properties[key] = create_swagger_definition(f"{schema_name}{key}", "object", value)
            elif isinstance(value, list):
                properties[key] = {
                    "type": "array",
                    "items": create_swagger_definition(f"{schema_name}{key}", "object", value[0])
                }
            else:
                properties[key] = {"type": f"{TYPE_MAPPING.get(type(value).__name__, type(value).__name__.lower())}"}
        swagger_definition["properties"] = properties
    elif schema_type == "array":
        swagger_definition["items"] = create_swagger_definition(schema_name, "object", schema_data[0])
    return swagger_definition

def create_swagger_definitions(json_file):
    with open(json_file, 'r') as f:
        schema_data = json.load(f)

    swagger_definitions = {}
    for schema_name, schema in schema_data.items():
        if schema_name == 'request':
            request_definition = create_swagger_definition(f"{schema.get("name")}{schema_name.title()}", "object", schema["data"])
            swagger_definitions[f"{schema["name"]}Request"] = request_definition
        if schema_name == 'response':
            response_definition = create_swagger_definition(f"{schema.get("name")}{schema_name.title()}", "object", schema["data"])
            swagger_definitions[f"{schema["name"]}Response"] = response_definition

    return swagger_definitions

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file", required=True, help="JSON file containing schema data")

    args = parser.parse_args()

    swagger_definitions = create_swagger_definitions(args.json_file)

    pyclip.copy(
        yaml.dump({"definitions": swagger_definitions}, default_flow_style=False, sort_keys=False)
    )
    print("Generated Swagger definitions copied to clipboard...")