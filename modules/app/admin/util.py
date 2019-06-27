from flask_admin.model import typefmt
import datetime
from flask import Markup
import pytz

_timezone = pytz.timezone('US/Pacific')


def localize(dt):
    return pytz.utc.localize(dt, is_dst=None).astimezone(_timezone)


def _date_format(view, value):
    loc = localize(value)
    return loc.strftime("%Y-%m-%d %H:%M:%S %Z")

def _list_format(view, values):
    return Markup('<br/>'.join(values))


defaultfmt = dict(typefmt.BASE_FORMATTERS)
defaultfmt.update({
    datetime.datetime: _date_format,
    list: _list_format
})
