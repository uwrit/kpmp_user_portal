from modules.app import mongo
from wtforms import fields, validators, form
from flask_admin.contrib.pymongo import ModelView
from flask_admin.model.template import BaseListRowAction
from .fields import ReadonlyDateTimeField, ReadonlyStringField, ShibIDField
from .util import defaultfmt, localize
from modules.app import groups
from flask import request
from modules.logger import log
from modules.app.diff import has_model_changed
import datetime

def _get_org_refs():
    return [
        (str(o.get('_id')), o.get('name')) for o in mongo.db.orgs.find()]


class SuspendRowAction(BaseListRowAction):
    def __init__(self, title=None):
        return super().__init__(title=title)

class UserForm(form.Form):
    shib_id = ShibIDField('Shibboleth ID')
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
    groups = fields.FieldList(ReadonlyStringField(''))
    active = fields.BooleanField('Active', default=lambda: True)
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])

class UserView(ModelView):
    column_list = ('shib_id', 'first_name',
                   'last_name', 'email', 'groups', 'role', 'org_name', 'active', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('shib_id', 'first_name',
                            'last_name', 'email', 'groups', 'role', 'org_name')
    column_type_formatters = defaultfmt

    column_searchable_list = ('last_name', 'first_name', 'email', 'shib_id')
    column_labels = dict(org_name='Organization')

    # column_extra_row_actions = []
    
    form = UserForm

    # Enables csv export of users
    can_export = True

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        try:
            ls = super().get_list(page, sort_column, sort_desc, search, filters, execute=execute, page_size=page_size)
            users: Iterable[Dict] = ls[1]
            to_search = [g.get('group_id') for g in mongo.db.groups.find({})]
            gs = groups.get_for_many([u.get('shib_id') for u in users], to_search)

            orgs_dict = {x[0]: x[1] for x in _get_org_refs()}

            for user in users:
                user['groups'] = gs.get(user.get('shib_id'))
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
                     remote_user=request.remote_user, id=model.get('_id'))
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update user", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def delete_model(self, model):
        try:
            log.info("deleting user",
                     remote_user=request.remote_user, id=model.get('_id'))
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete user", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.organization_id.choices = _get_org_refs()
        return form

    def edit_form(self, obj: dict = None):
        if obj.get('last_changed_on'):
            obj['last_changed_on'] = localize(obj.get('last_changed_on'))
        to_search = to_search = [g.get('group_id') for g in mongo.db.groups.find({})]
        obj['groups'] = groups.get_for_one(obj.get('shib_id'), to_search)

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
        old = mongo.db.users.find_one({'_id': model.get('_id')})
        if has_model_changed(old, model):
            old['id'] = old.get('_id')
            del old['_id']
            old['action'] = action
            log.info("archiving user record",
                     id=old.get('id'), action=action, remote_user=request.remote_user)
            mongo.db.users_archive.insert_one(old)
