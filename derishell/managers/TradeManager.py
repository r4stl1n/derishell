import time
from derishell.util.deribit_api import RestClient

from derishell.util.Util import Util
from derishell.managers.ConfigManager import ConfigManager
from derishell.managers.DatabaseManager import DatabaseManager

class TradeManager:

    @staticmethod
    def create_new_buy_order(price, amount):
        Util.get_logger().info("Placing Buy Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.buy(ConfigManager.get_config().tradeInsturment, amount, price, False, "")
        return order

    @staticmethod
    def create_new_sell_order(price, amount):
        Util.get_logger().info("Placing Sell Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.sell(ConfigManager.get_config().tradeInsturment, amount, price, True, "")
        return order

    @staticmethod
    def setup_inital_ladder():
        Util.get_logger().info("Setup initial ladder")

        for x in range(ConfigManager.get_config().numOfOrders):
            DatabaseManager.create_order_entry("", (ConfigManager.get_config().basePrice - ConfigManager.get_config().priceDistance) - (ConfigManager.get_config().priceDistance * x), ConfigManager.get_config().contractSize, "buy")

        TradeManager.update_pending_orders()

    @staticmethod
    def cancel_all_current_orders():

        orders = DatabaseManager.get_all_open_orders()
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

        for order in orders:
            client.cancel(order.orderId)
            DatabaseManager.update_order_entry(order.orderId, "cancelled")
            Util.get_logger().info("Cancelled order: " + str(order.orderId))


    @staticmethod
    def close_all_positions():
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        positions = client.positions()

        for x in positions:
            if x['direction'] == 'buy':
                client.sell(ConfigManager.get_config().tradeInsturment, x['size'], 1, False, "")
            else:
                client.buy(ConfigManager.get_config().tradeInsturment, x['size'], 99999, False, "")

    @staticmethod
    def update_pending_orders():

        orders = DatabaseManager.get_all_pending_orders()
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

        for order in orders:

            currentPrice = client.getsummary(ConfigManager.get_config().tradeInsturment)['askPrice']

            if order.direction == 'buy':
                if currentPrice > order.price:
                    newOrder = TradeManager.create_new_buy_order(order.price, order.contractSize)
                    DatabaseManager.update_new_order_entry(order, newOrder['order']['orderId'], "open")

            else:
                newOrder = TradeManager.create_new_sell_order(order.price, order.contractSize)
                DatabaseManager.update_new_order_entry(order, newOrder['order']['orderId'], "open")


    @staticmethod
    def update_order_status():

        orders = DatabaseManager.get_all_open_orders()

        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

        for order in orders:

            try:
                
                updatedOrder = client.getorderstate(order.orderId)

                DatabaseManager.update_order_entry(order.orderId, updatedOrder['state'])

                if updatedOrder['state'] == "filled":

                    if updatedOrder['direction'] == "buy":

                        if ConfigManager.get_config().fcbMode:
                            #Create new one
                            DatabaseManager.create_order_entry("", order.price + ConfigManager.get_config().priceDistance, ConfigManager.get_config().contractSize, "sell")

                        else:
                            sellPriceOffset = ConfigManager.get_config().basePrice - order.price
                            DatabaseManager.create_order_entry("", ConfigManager.get_config().basePrice + sellPriceOffset, ConfigManager.get_config().contractSize, "sell")

                    else:

                        if ConfigManager.get_config().fcbMode:
                            DatabaseManager.create_order_entry("", order.price - ConfigManager.get_config().priceDistance, ConfigManager.get_config().contractSize, "buy")
                        else:
                            # put in buy order
                            buyPriceOffset = order.price - ConfigManager.get_config().basePrice
                            DatabaseManager.create_order_entry("",ConfigManager.get_config().basePrice + buyPriceOffset , ConfigManager.get_config().contractSize, "buy")
            except:
                pass

    @staticmethod
    def update_all():
        TradeManager.update_order_status()
        TradeManager.update_pending_orders()

                
