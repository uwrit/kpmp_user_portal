# Deployment
This app is intended to be deployed behind Apache with mod_wsgi, additionally, we use Shibboleth to implement federated authentication.

## Python
Ensure python3.6+ is installed.
```bash
cd /data
mkdir userportal
cd userportal
git clone https://github.com/uwrit/kpmp_user_portal.git
cd kpmp_user_portal
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

## WSGI
Create /data/userportal/portal.wsgi
```python
activate_this = '/data/userportal/kpmp_user_portal/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/data/userportal')
sys.path.insert(0, '/data/userportal/kpmp_user_portal')

from kpmp_user_portal import app as application
```

## Apache
Create /data/userportal/users.conf
```
kpmpuseradmins: eppns...
```

```xml
<VirtualHost *:443>
    ...Server and SSL config elided
    <Files *.sso>
        SetHandler shib-handler
    </Files>

    WSGIDaemonProcess uport user={user} python-home=/data/userportal/kpmp_user_portal/venv python-path=/data/userportal/kpmp_user_portal:/data/userportal/kpmp_user_portal/venv/lib/python3.6/site-packages
    WSGIProcessGroup uport
    WSGIScriptAlias / /data/userportal/portal.wsgi

    <Location /Shibboleth.sso>
      SetHandler shib
    </Location>

    <Location /admin>
      <RequireAll>
        AuthType shibboleth
        ShibRequestSetting requireSession 1
        AuthGroupFile /data/userportal/users.conf
        require group kpmpuseradmins
      </RequireAll>
    </Location>

</VirtualHost>
```
