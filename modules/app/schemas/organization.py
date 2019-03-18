from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

_org_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "care_of": {
            "type": "string"
        },
        "street": {
            "type": "string"
        },
        "city": {
            "type": "string"
        },
        "state": {
            "type": "string"
        },
        "postal_code": {
            "type": "string"
        }
    },
    "required": ["name"]
}


def validate_org(data):
    try:
        validate(data, _org_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
