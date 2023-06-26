from typing import Any, Tuple

from wtforms import (
    Form,
    StringField,
    IntegerField,
    FloatField,
    BooleanField,
    SelectField,
    FileField,
    validators,
)

field_name_to_type_map = {
    "integer": IntegerField,
    "float": FloatField,
    "string": StringField,
    "boolean": BooleanField,
    "file": FileField,
    "dropdown": SelectField,
}


def form_from_defn(defn_list: Tuple[Any, Any, Any, Any]) -> Form:
    """
    this will have to be refactored when we have a better idea of exactly the defn list format
    """
    form = Form()
    print(defn_list)
    field_label, field_type, default_value, is_required = defn_list

    print(field_label, field_type, default_value, is_required)
    try:
        field_class = field_name_to_type_map[field_type]
    except KeyError:
        raise KeyError(f"invalid field type {field_type}")

    validators_list = [validators.InputRequired()] if is_required else []

    if field_label == "dropdown":
        # TODO escape
        [choice.strip() for choice in default_value.split(",")]
        field = field_class(
            label=field_label, validators=validators_list, choices=default_value
        )
    else:
        field = field_class(
            label=field_label, validators=validators_list, default=default_value
        )

    setattr(form, field_label, field)
    return form
