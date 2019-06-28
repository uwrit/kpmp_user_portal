from modules.app import mongo
from wtforms import fields, validators, form
from flask_admin.contrib.pymongo import ModelView
from .fields import ReadonlyDateTimeField, ReadonlyStringField
from .util import defaultfmt
from flask import request
from modules.logger import log
from modules.app.diff import has_model_changed
import datetime

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
    column_type_formatters = defaultfmt

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
                     id=model.get('_id'))
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update org", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def delete_model(self, model):
        try:
            log.info("deleting org", remote_user=request.remote_user,
                     id=model.get('_id'))
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete org", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
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
        old = mongo.db.orgs.find_one({'_id': model.get('_id')})
        if has_model_changed(old, model):
            old['id'] = old.get('_id')
            del old['_id']
            old['action'] = action
            log.info("archiving org record",
                     id=old.get('id'), action=action, remote_user=request.remote_user)
            mongo.db.orgs_archive.insert_one(old)
