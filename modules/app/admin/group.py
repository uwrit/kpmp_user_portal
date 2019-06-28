from wtforms import fields, validators, form
from flask_admin.contrib.pymongo import ModelView
from .fields import ReadonlyDateTimeField, ReadonlyStringField
from .util import defaultfmt
from flask import request
from modules.logger import log
import datetime

class GroupForm(form.Form):
    group_id = fields.StringField('Group ID', [validators.DataRequired()])
    last_changed_by = ReadonlyStringField(
        'Last Changed By', [validators.Optional()])
    last_changed_on = ReadonlyDateTimeField(
        'Last Changed On', [validators.Optional()])

class GroupView(ModelView):
    column_list = ('group_id', 'last_changed_by', 'last_changed_on')
    column_sortable_list = ('group_id')
    column_type_formatters = defaultfmt

    form = GroupForm

    def create_model(self, form):
        try:
            return super().create_model(form)
        except Exception as e:
            log.error("could not create group", exc_info=e,
                      remote_user=request.remote_user)
            raise

    def update_model(self, form, model):
        try:
            log.info("updating group", remote_user=request.remote_user,
                     id=model.get('_id'))
            return super().update_model(form, model)
        except Exception as e:
            log.error("could not update group", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def delete_model(self, model):
        try:
            log.info("deleting group", remote_user=request.remote_user,
                     id=model.get('_id'))
            return super().delete_model(model)
        except Exception as e:
            log.error("could not delete group", exc_info=e,
                      remote_user=request.remote_user, id=model.get('_id'))
            raise

    def on_model_change(self, form, model, is_created):
        model['last_changed_by'] = request.remote_user
        model['last_changed_on'] = datetime.datetime.utcnow()
        return super().on_model_change(form, model, is_created)
