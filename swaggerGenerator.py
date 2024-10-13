import argparse
import yaml
import pyclip
import os


def create_swagger_endpoint(
    method,
    tag,
    description,
    summary,
    operation_id,
    service_name,
    domain,
    schema_name,
    parameters,
):
   
    swagger_template = {
        method: {
            "tags": [tag],
            "security": [{"bearerAuth": []}],
            "description": description,
            "summary": summary,
            "operationId": operation_id,
            "x-google-backend": {
                "address": f"https://{service_name}-{domain}",
                "path_translation": "APPEND_PATH_TO_ADDRESS",
            },
            "parameters": [],
            "responses": {
                "200": {
                    "description": "A successful response",
                    "schema": {"$ref": f"#/definitions/{schema_name}Response"},
                }
            },
            "options": {
                "tags": ["cors"],
                "summary": f"Option {method} {summary}",
                "operationId": f"cors-{operation_id}",
                "x-google-backend": {
                    "address": f"https://{service_name}-{domain}",
                    "path_translation": "APPEND_PATH_TO_ADDRESS",
                },
                "parameters": [],
                "responses": {
                    "200": {
                        "description": "A successful response",
                        "schema": {"$ref": f"#/definitions/{schema_name}Response"},
                    }
                },
            },
        }
    }
    
    if schema_name:
        swagger_template[method]["parameters"].append(
            {
                "in": "body",
                "name": "body",
                "required": True,
                "schema": {"$ref": f"#/definitions/{schema_name}Request"},
            }
        )
   
    for param in parameters:
        swagger_template[method]["parameters"].append(
            {
                "name": param,
                "in": "path",
            }
        )
        swagger_template[method]["options"]["parameters"].append(
            {
                "name": param,
                "in": "path",
            }
        )
        
    return swagger_template


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--method", required=True, help="Method of the endpoint (e.g. GET, POST, etc.)"
    )
    parser.add_argument("--tag", required=True, help="Tag of the endpoint")
    parser.add_argument(
        "--description", required=True, help="Description of the endpoint"
    )
    parser.add_argument("--summary", required=True, help="Summary of the endpoint")
    parser.add_argument(
        "--operation-id", required=True, help="Operation ID of the endpoint"
    )
    parser.add_argument(
        "--service-name", required=True, help="Service name of the endpoint"
    )
    parser.add_argument("--domain", required=True, help="Domain of the endpoint")
    parser.add_argument(
        "--schema-name", required=False, help="Schema name of the endpoint"
    )
    parser.add_argument("--parameters", required=False, nargs='+', help="Parameters of the endpoint (e.g. companyId userId)")

    args = parser.parse_args()

   
    swagger_endpoint = create_swagger_endpoint(
        args.method,
        args.tag,
        args.description,
        args.summary,
        args.operation_id,
        args.service_name,
        args.domain,
        args.schema_name,
        args.parameters,
    )

    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    pyclip.copy(
        yaml.dump(
            swagger_endpoint, Dumper=MyDumper, default_flow_style=False, sort_keys=False
        )
    )
    os.system('cls')
    print("Generated Swagger endpoint copied to clipboard...")
