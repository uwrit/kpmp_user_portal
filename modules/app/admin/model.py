from flask_admin import Admin
from flask_admin.model import typefmt
from wtforms import form, fields, validators
from flask_admin.contrib.pymongo import ModelView
from flask import request, Markup
from modules.app import mongo, app
from modules.app.diff import has_model_changed
import uuid
import datetime
import pytz
from flask_pymongo import ObjectId
from modules.logger import log
from modules.app import groups

_timezone = pytz.timezone('US/Pacific')


def _localize(dt):
    return pytz.utc.localize(dt, is_dst=None).astimezone(_timezone)


def _date_format(view, value):
    loc = _localize(value)
    return loc.strftime("%Y-%m-%d %H:%M:%S %Z")

def _list_format(view, values):
    return Markup('<br/>'.join(values))


_formatters = dict(typefmt.BASE_FORMATTERS)
_formatters.update({
    datetime.datetime: _date_format,
    list: _list_format
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
    groups = fields.FieldList(fields.StringField(''))
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])

class UserView(ModelView):
    column_list = ('shib_id', 'first_name',
                   'last_name', 'email', 'groups', 'role', 'org_name','last_changed_by', 'last_changed_on')
    column_sortable_list = ('shib_id', 'first_name',
                            'last_name', 'email', 'groups', 'role', 'org_name')
    column_type_formatters = _formatters

    column_searchable_list = ('last_name', 'first_name', 'email', 'shib_id')
    column_labels = dict(org_name='Organization')
    
    form = UserForm

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        try:
            ls = super().get_list(page, sort_column, sort_desc, search, filters, execute=execute, page_size=page_size)
            users: Iterable[Dict] = ls[1]
            to_search = [g['group_id'] for g in mongo.db.groups.find({})]
            gs = groups.get_for_many([u['shib_id'] for u in users], to_search)

            orgs_dict = {str(x['_id']): x['name'] for x in mongo.db.orgs.find()}

            for user in users:
                user['groups'] = gs.get(user['shib_id'])
                org_id = user.get('organization_id')
                if org_id:
                    user['org_name'] = orgs_dict.get(org_id, "Unknown ({})".format(org_id))

            return ls
        except Exception as e:
            log.error("could not list memberships", exc_info=e,
                      remote_user=request.remote_user)
            raise

    def create_model(self, form):
        try:
            return super().create_model(form)
        except Exception as e:
            log.error("could not create user", exc_info=e,
                      remote_user=request.remote_user)
            raise

    def update_model(self, form, model):
        try:
            log.info("updating user",
                     remote_user=request.remote_user, id=model['_id'])
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update user", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def delete_model(self, model):
        try:
            log.info("deleting user",
                     remote_user=request.remote_user, id=model['_id'])
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete user", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.organization_id.choices = _get_org_refs()
        return form

    def edit_form(self, obj: dict = None):
        if obj.get('last_changed_on'):
            obj['last_changed_on'] = _localize(obj['last_changed_on'])
        to_search = to_search = [g['group_id'] for g in mongo.db.groups.find({})]
        obj['groups'] = groups.get_for_one(obj['shib_id'], to_search)

        form = super().edit_form(obj)
        form.organization_id.choices = _get_org_refs()

        if obj.get('phone_numbers') and len(obj.get('phone_numbers')) >= form.phone_numbers.min_entries:
            form.phone_numbers.append_entry()

        if obj.get('fax_numbers') and len(obj.get('fax_numbers')) >= form.fax_numbers.min_entries:
            form.fax_numbers.append_entry()

        return form

    def validate_form(self, form):
        if hasattr(form, 'organization_id'):
            form.organization_id.choices = _get_org_refs()
        return super().validate_form(form)

    def on_model_change(self, form, model: dict, is_created):
        model['phone_numbers'] = [
            pn for pn in model.get('phone_numbers', []) if pn]
        model['fax_numbers'] = [
            fn for fn in model.get('fax_numbers', []) if fn]
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model, 'update')
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        self._archive_model(model, 'delete')
        return super().on_model_delete(model)

    def _archive_model(self, model, action):
        old = mongo.db.users.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            old['id'] = old['_id']
            del old['_id']
            old['action'] = action
            log.info("archiving user record",
                     id=old['id'], action=action, remote_user=request.remote_user)
            mongo.db.users_archive.insert_one(old)


class ClientForm(form.Form):
    name = fields.StringField('Name', [validators.DataRequired()])
    owner = fields.StringField('Owner', [validators.DataRequired()])
    owner_email = fields.StringField(
        'Email', [validators.DataRequired(), validators.Email()])
    token = ReadonlyStringField(
        'Token', [validators.DataRequired()], default=lambda: str(uuid.uuid4()))
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])


class ClientView(ModelView):
    column_list = ('name', 'owner', 'owner_email',
                   'last_changed_by', 'last_changed_on')
    column_sortable_list = ('name', 'owner')
    column_type_formatters = _formatters

    form = ClientForm

    def create_model(self, form):
        try:
            return super().create_model(form)
        except Exception as e:
            log.error("could not create client", exc_info=e,
                      remote_user=request.remote_user)
            raise

    def update_model(self, form, model):
        try:
            log.info("updating client",
                     remote_user=request.remote_user, id=model['_id'])
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update client", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def delete_model(self, model):
        try:
            log.info("deleting client",
                     remote_user=request.remote_user, id=model['_id'])
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete client", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model, 'update')
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        self._archive_model(model, 'delete')
        return super().on_model_delete(model)

    def _archive_model(self, model, action):
        old = mongo.db.clients.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            old['id'] = old['_id']
            del old['_id']
            old['action'] = action
            log.info("archiving client record",
                     id=old['id'], action=action, remote_user=request.remote_user)
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

    def create_model(self, form):
        try:
            return super().create_model(form)
        except Exception as e:
            log.error("could not create org", exc_info=e,
                      remote_user=request.remote_user)
            raise

    def update_model(self, form, model):
        try:
            log.info("updating org", remote_user=request.remote_user,
                     id=model['_id'])
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update org", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def delete_model(self, model):
        try:
            log.info("deleting org", remote_user=request.remote_user,
                     id=model['_id'])
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete org", exc_info=e,
                      remote_user=request.remote_user, id=model['_id'])
            raise

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        if not is_created:
            self._archive_model(model, 'update')
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        self._archive_model(model, 'delete')
        return super().on_model_delete(model)

    def _archive_model(self, model, action):
        old = mongo.db.orgs.find_one({'_id': model['_id']})
        if has_model_changed(old, model):
            old['id'] = old['_id']
            del old['_id']
            old['action'] = action
            log.info("archiving org record",
                     id=old['id'], action=action, remote_user=request.remote_user)
            mongo.db.orgs_archive.insert_one(old)

class GroupForm(form.Form):
    group_id = fields.StringField('Group ID', [validators.DataRequired()])
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])

class GroupView(ModelView):
    column_list = ('group_id', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('group_id')
    column_type_formatters = _formatters

    form = GroupForm

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        return super().on_model_change(form, model, is_created)

admin = Admin(app, name='KPMP User Portal Admin Panel')
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(OrganizationView(mongo.db.orgs, 'Organizations'))
admin.add_view(GroupView(mongo.db.groups, 'Groups'))
admin.add_view(ClientView(mongo.db.clients, 'Clients'))
