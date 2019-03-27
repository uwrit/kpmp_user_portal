from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

_org_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "code": {
            "type": "string"
        },
        "short_name": {
            "type": "string"
        },
        "care_of": {
            "type": "string"
        },
        "street": {
            "type": "string"
        },
        "extended_address": {
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
        },
        "country_name": {
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
    "required": ["name"],
    "dependencies": {
        "extended_address": ["street_address"]
    }
}


def validate_org(data):
    try:
        validate(data, _org_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
