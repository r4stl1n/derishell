from derishell.models.OrderModel import OrderModel

from derishell.util.Util import Util
from derishell.util.Database import internal_database

class DatabaseManager:

    def __init__(self):
        pass

    @staticmethod
    def initalize():
        internal_database.connect()
        internal_database.create_tables([OrderModel])

    @staticmethod
    def create_order_entry(orderid, price, contractsize, direction):
        
        orderModel = OrderModel()
        orderModel.orderId = orderid
        orderModel.contractSize = contractsize
        orderModel.price = price
        orderModel.status = "Open"
        orderModel.direction = direction
        orderModel.save()

        return orderModel
        

    @staticmethod
    def update_order_entry(orderid, status):
        
        try:

            orderModel = OrderModel.get(OrderModel.orderId == orderid)
            orderModel.status = status
            orderModel.save()

            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None

    @staticmethod
    def update_sell_order_entry(orderid, amount):
        try:

            orderModel = OrderModel.get(OrderModel.orderId == orderid)
            orderModel.amount = amount
            orderModel.save()

            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None  

    @staticmethod
    def get_order_by_id(orderid):

        try:

            orderModel = OrderModel.get(OrderModel.orderid == orderid)
            return orderModel

        except:

            Util.get_logger().debug("Failed to retrieve order: " + str(orderid))
            return None

    @staticmethod
    def get_all_orders():
        return OrderModel.select()

    @staticmethod
    def get_all_open_orders():
        return OrderModel.select().where(OrderModel.status == 'Open')

    @staticmethod
    def get_open_sell_order():
        try:
            return OrderModel.select().where(OrderModel.status == 'Open' & OrderModel.direction == "sell")
        except:
            return None