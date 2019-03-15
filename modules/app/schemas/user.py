from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

_user_schema = {
    "type": "object",
    "properties": {
        "first_name": {
            "type": "string"
        },
        "last_name": {
            "type": "string"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "phone_numbers": {
            "type": "array",
            "items": {"type": "string"}
        },
        "fax_numbers": {
            "type": "array",
            "items": {"type": "string"}
        },
        "role": {
            "type": "string"
        },
        "job_title": {
            "type": "string"
        },
        "organization_id": {
            "type": "string"
        }
    },
    "required": ["first_name", "last_name"]
}


def validate_user(data):
    try:
        validate(data, _user_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
