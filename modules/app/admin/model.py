from flask_admin import Admin
from modules.app import mongo, app
from .user import UserView
from .client import ClientView
from .org import OrganizationView
from .group import GroupView

admin = Admin(app, name='KPMP User Portal Admin Panel')
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(OrganizationView(mongo.db.orgs, 'Organizations'))
admin.add_view(GroupView(mongo.db.groups, 'Groups'))
admin.add_view(ClientView(mongo.db.clients, 'Clients'))
