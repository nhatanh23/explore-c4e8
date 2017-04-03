from mongoengine import *


class CarItems(Document):
    src = StringField()
    title = StringField()
    description = StringField()
