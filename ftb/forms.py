from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import Form, StringField, PasswordField, SubmitField, SelectField


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("login")


"""
https://www.sqlalchemy.org/
"""

""" Metadata Forms

trying to reason through metadata forms; there is a specific hierarchy
of required and optional fields, fields that users vs. admins vs. website
admins can edit, etc.

Three classes of fields:
    - Mandatory: set by website admin, cannot be edited by any user
        - e.g. user org, internal ids, etc
    - Admin Compulsory: set by user admin, field testers must fill out
        - e.g. project name, location, fields, e.t.c.
    - Admin Optional: set by user admin, field testers can fill out
        - e.g. notes
"""


class MandatoryFieldTestForm(Form):
    """Base Form for Field Test

    The fields below act as the base for all field test forms. When we get
    a field test from the db, we add the fields to the form that the field
    tester have to fill out and then render the form.

    Some (most?) fields we don't render, though, since it's not an option for the
    user (such as `organization`). Not sure if defining a field over another
    type of variable is the way to go?

    CSRF is disabled for this subform because it is never used by itself.

    how to create dynamic forms
    https://wtforms.readthedocs.io/en/2.3.x/specific_problems/#dynamic-form-composition
    """

    organization = StringField("organization", validators=[DataRequired()])
    submit = SubmitField("submit")


class FieldTestForm(FlaskForm):
    """Form for Field Test

    Defined by the Admin, contains compulsory and non-compulsary fields.
    This must be built from the Admin's form definition - therefore, we
    build this form dynamically for each fied test that they define. The
    only mandatory field (for now) is the field test type.
    """

    field_test_type = SelectField("field_test_type", choices=[])
    submit = SubmitField("submit")


class CreateFieldTestForm(FlaskForm):
    """Form for Creating Field Test

    This is the form that the Admin uses to create a field test. The field_test_type
    is mandatory, as it is the name for the field test (e.g. "Pedal Kickback Reqs").
    The rest of the fields must be defined dynamically by the admin (i.e. the admin
    is adding fields and their types to build this type of form!).

    Guide for building this functionality
    https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/
    """

    field_test_type = StringField("field test type", validators=[DataRequired()])
    submit = SubmitField("submit")
