from wtforms import fields

class ReadonlyStringField(fields.StringField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyStringField, self).__call__(*args, **kwargs)


class ReadonlyDateTimeField(fields.DateTimeField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('readonly', True)
        return super(ReadonlyDateTimeField, self).__call__(*args, **kwargs)

class ShibIDField(fields.StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].lower()
        else:
            self.data = ''