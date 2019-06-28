from modules.app import mongo
from wtforms import fields, validators, form
from flask_admin.contrib.pymongo import ModelView
from .fields import ReadonlyDateTimeField, ReadonlyStringField
from .util import defaultfmt
from flask import request
from modules.logger import log
from modules.app.diff import has_model_changed
import datetime
import uuid


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
    column_type_formatters = defaultfmt

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
                     remote_user=request.remote_user, id=model.get('_id'))
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update client", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def delete_model(self, model):
        try:
            log.info("deleting client",
                     remote_user=request.remote_user, id=model.get('_id'))
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete client", exc_info=e,
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
        old = mongo.db.clients.find_one({'_id': model.get('_id')})
        if has_model_changed(old, model):
            old['id'] = old.get('_id')
            del old['_id']
            old['action'] = action
            log.info("archiving client record",
                     id=old.get('id'), action=action, remote_user=request.remote_user)
            mongo.db.clients_archive.insert_one(old)
