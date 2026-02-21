from jsonschema import validate, ValidationError


class SchemaValidation(Exception):
    pass

def validate_schema(data:dict,schema:dict):
    try:
        validate(instance=data,schema=schema)
    except ValidationError as e:
        raise SchemaValidation(str(e))