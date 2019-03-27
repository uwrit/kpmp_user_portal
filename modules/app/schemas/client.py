from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

_client_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "token": {
            "type": "string"
        },
        "last_changed_by": {
            "type": "string"
        },
        "last_changed_on": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["name", "token"]
}


def validate_client(data):
    try:
        validate(data, _client_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
