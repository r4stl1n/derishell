import datetime
from peewee import *
from derishell.util.Database import internal_database

class OrderModel(Model):

    contractSize = IntegerField(default=0)
    orderId = CharField(default="")
    price = DoubleField(default=0.0)
    direction = CharField(default="")
    status = CharField(default="")
    iuid = CharField(default="")
    createdDate = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = internal_database