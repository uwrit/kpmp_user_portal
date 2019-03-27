from flask_admin import Admin
from flask_admin.model import typefmt
from wtforms import form, fields, validators
from flask_admin.contrib.pymongo import ModelView
from flask import request
from modules.app import mongo, app
from modules.app.diff import has_model_changed
import uuid
import datetime
import pytz
from flask_pymongo import ObjectId

_timezone = pytz.timezone('US/Pacific')


def _localize(dt):
    return pytz.utc.localize(dt, is_dst=None).astimezone(_timezone)


def _date_format(view, value):
    loc = _localize(value)
    return loc.strftime("%Y-%m-%d %H:%M:%S %Z")


_formatters = dict(typefmt.BASE_FORMATTERS)
_formatters.update({
    datetime.datetime: _date_format
})


class ReadonlyStringField(fields.StringField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyStringField, self).__call__(*args, **kwargs)


class ReadonlyDateTimeField(fields.DateTimeField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyDateTimeField, self).__call__(*args, **kwargs)


def _get_org_refs():
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
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])


class UserView(ModelView):
    column_list = ('shib_id', 'first_name',
                   'last_name', 'email', 'phone_numbers', 'fax_numbers', 'role', 'job_title', 'organization_id', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('shib_id', 'first_name',
                            'last_name', 'email', 'role')
    column_type_formatters = _formatters

    form = UserForm

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.organization_id.choices = _get_org_refs()
        return form

    def edit_form(self, obj=None):
        if obj.get('last_changed_on'):
            obj['last_changed_on'] = _localize(obj['last_changed_on'])

        form = super().edit_form(obj)
        form.organization_id.choices = _get_org_refs()

        if len(obj['phone_numbers']) >= form.phone_numbers.min_entries:
            form.phone_numbers.append_entry()

        if len(obj['fax_numbers']) >= form.fax_numbers.min_entries:
            form.fax_numbers.append_entry()

        return form

    def validate_form(self, form):
        if hasattr(form, 'organization_id'):
            form.organization_id.choices = _get_org_refs()
        return super().validate_form(form)

    def on_model_change(self, form, model, is_created):
        model['phone_numbers'] = [pn for pn in model['phone_numbers'] if pn]
        model['fax_numbers'] = [fn for fn in model['fax_numbers'] if fn]
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model)
        return super().on_model_change(form, model, is_created)

    def _archive_model(self, model):
        old = mongo.db.users.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            print('archiving')
            old['id'] = old['_id']
            del old['_id']
            mongo.db.users_archive.insert_one(old)


class ClientForm(form.Form):
    name = fields.StringField('Name', [validators.DataRequired()])
    token = ReadonlyStringField(
        'Token', [validators.DataRequired()], default=lambda: str(uuid.uuid4()))
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])


class ClientView(ModelView):
    column_list = ('name', 'token', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('name',)
    column_type_formatters = _formatters

    form = ClientForm

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model)
        return super().on_model_change(form, model, is_created)

    def _archive_model(self, model):
        old = mongo.db.clients.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            old['id'] = old['_id']
            del old['_id']
            mongo.db.clients_archive.insert_one(old)


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
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])

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
                   'extended_address', 'city', 'state', 'postal_code', 'country_name', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('name', 'city', 'state', 'code')
    column_type_formatters = _formatters

    form = OrganizationForm

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model)
        return super().on_model_change(form, model, is_created)

    def _archive_model(self, model):
        old = mongo.db.orgs.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            old['id'] = old['_id']
            del old['_id']
            mongo.db.orgs_archive.insert_one(old)


admin = Admin(app, name='KPMP User Portal Admin Panel')
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(OrganizationView(mongo.db.orgs, 'Organizations'))
admin.add_view(ClientView(mongo.db.clients, 'Clients'))
