from flask_admin import Admin

from wtforms import form, fields, validators

from flask_admin.contrib.pymongo import ModelView
from modules.app import mongo, app
import uuid
from flask_pymongo import ObjectId


def get_org_refs():
    return [
        (str(o.get('_id')), o.get('name')) for o in mongo.db.orgs.find()]


class UserForm(form.Form):
    shib_id = fields.StringField('Shibboleth ID')
    first_name = fields.StringField('First name', [validators.DataRequired()])
    last_name = fields.StringField('Last name', [validators.DataRequired()])
    email = fields.StringField(
        'Email', [validators.Optional(), validators.Email()])
    phone_numbers = fields.FieldList(
        fields.StringField(''), min_entries=1)
    fax_numbers = fields.FieldList(
        fields.StringField(''), min_entries=1)
    role = fields.StringField('Role')
    job_title = fields.StringField('Job Title')
    organization_id = fields.SelectField('Organization')


class UserView(ModelView):
    column_list = ('shib_id', 'first_name',
                   'last_name', 'email', 'phone_numbers', 'fax_numbers', 'role', 'job_title', 'organization_id')
    column_sortable_list = ('shib_id', 'first_name',
                            'last_name', 'email', 'role')

    form = UserForm

    def create_form(self, obj=None):
        form = super(UserView, self).create_form(obj)
        form.organization_id.choices = get_org_refs()
        return form

    def edit_form(self, obj=None):
        form = super(UserView, self).edit_form(obj)
        form.organization_id.choices = get_org_refs()

        if len(obj['phone_numbers']) >= form.phone_numbers.min_entries:
            form.phone_numbers.append_entry()

        if len(obj['fax_numbers']) >= form.fax_numbers.min_entries:
            form.fax_numbers.append_entry()

        return form

    def validate_form(self, form):
        if hasattr(form, 'organization_id'):
            form.organization_id.choices = get_org_refs()
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
    short_name = fields.StringField('Short Name for Org')
    code = fields.StringField('Org Code')
    care_of = fields.StringField('Care of')
    street = fields.StringField('Street')
    extended_address = fields.StringField('Extended Address')
    city = fields.StringField('City')
    state = fields.StringField('State')
    postal_code = fields.StringField('Postal Code')
    country_name = fields.SelectField('Country',
                                      choices=[
                                          ('', ''), ('United States', 'United States'), ('United Kingdom', 'United Kingdom')]
                                      )

    def validate(self):
        rv = super(OrganizationForm, self).validate()
        if not rv:
            return False

        if self.extended_address.data and not self.street.data:
            self.extended_address.errors.append(
                "Street required to define extended")
            return False
        return rv


class OrganizationView(ModelView):
    column_list = ('name', 'short_name', 'code', 'care_of', 'street',
                   'extended_address', 'city', 'state', 'postal_code', 'country_name')
    column_sortable_list = ('name', 'city', 'state', 'code')

    form = OrganizationForm


admin = Admin(app, name='KPMP User Portal Admin Panel')
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(OrganizationView(mongo.db.orgs, 'Organizations'))
admin.add_view(ClientView(mongo.db.clients, 'Clients'))
