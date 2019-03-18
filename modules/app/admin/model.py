from flask_admin import Admin

from wtforms import form, fields, validators

from flask_admin.form import Select2Widget
from flask_admin.contrib.pymongo import ModelView, filters
from flask_admin.model.fields import FormField
from modules.app import mongo, app
import uuid
from flask_pymongo import ObjectId


class UserForm(form.Form):
    targetted_id = fields.StringField('Targetted ID')
    eppn = fields.StringField('EPPN')
    first_name = fields.StringField('First name', [validators.DataRequired()])
    last_name = fields.StringField('Last name', [validators.DataRequired()])
    email = fields.StringField('Email', [validators.Email()])
    phone_numbers = fields.FieldList(
        fields.StringField(''), min_entries=1)
    fax_numbers = fields.FieldList(
        fields.StringField(''), min_entries=1)
    role = fields.StringField('Role')
    job_title = fields.StringField('Job Title')
    organization_id = fields.SelectField('Organization', coerce=ObjectId)


class UserView(ModelView):
    column_list = ('targetted_id', 'eppn', 'first_name',
                   'last_name', 'email', 'phone_numbers', 'fax_numbers', 'role', 'job_title', 'organization_id')
    column_sortable_list = ('eppn', 'first_name', 'last_name', 'email', 'role')

    form = UserForm

    def create_form(self, obj=None):
        form = super(UserView, self).create_form(obj)
        form.organization_id.choices = [
            (o.get('_id'), o.get('name')) for o in mongo.db.orgs.find()]
        return form

    def edit_form(self, obj=None):
        form = super(UserView, self).edit_form(obj)
        form.organization_id.choices = [
            (o.get('_id'), o.get('name')) for o in mongo.db.orgs.find()]

        if len(obj['phone_numbers']) >= form.phone_numbers.min_entries:
            form.phone_numbers.append_entry()

        if len(obj['fax_numbers']) >= form.fax_numbers.min_entries:
            form.fax_numbers.append_entry()

        return form

    def validate_form(self, form):
        if hasattr(form, 'organization_id'):
            form.organization_id.choices = [
                (o.get('_id'), o.get('name')) for o in mongo.db.orgs.find()]
        return super().validate_form(form)

    def on_model_change(self, form, model, is_created):
        model['phone_numbers'] = [pn for pn in model['phone_numbers'] if pn]
        model['fax_numbers'] = [fn for fn in model['fax_numbers'] if fn]
        return super().on_model_change(form, model, is_created)


class ClientForm(form.Form):
    name = fields.StringField('Name', [validators.DataRequired()])
    token = fields.StringField(
        'Token', [validators.DataRequired()], default=lambda: str(uuid.uuid4()))


class ClientView(ModelView):
    column_list = ('name', 'token')
    column_sortable_list = ('name',)

    form = ClientForm


class OrganizationForm(form.Form):
    name = fields.StringField('Name', [validators.DataRequired()])
    care_of = fields.StringField('Care of')
    street = fields.StringField('Street')
    city = fields.StringField('City')
    state = fields.StringField('State')
    postal_code = fields.StringField('Postal Code')


class OrganizationView(ModelView):
    column_list = ('name', 'care_of', 'street', 'city', 'state', 'postal_code')
    column_sortable_list = ('name', 'city', 'state')

    form = OrganizationForm


admin = Admin(app, name='KPMP User Portal Admin Panel')
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(OrganizationView(mongo.db.orgs, 'Organizations'))
admin.add_view(ClientView(mongo.db.clients, 'Clients'))
