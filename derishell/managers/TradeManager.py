import time
from derishell.util.deribit_api import RestClient

from derishell.util.Util import Util
from derishell.managers.ConfigManager import ConfigManager
from derishell.managers.DatabaseManager import DatabaseManager

class TradeManager:

    @staticmethod
    def create_new_buy_order(price, amount, postonly):
        Util.get_logger().info("Placing Buy Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.buy(ConfigManager.get_config().tradeInsturment, amount, price, postonly, "")
        return order

    @staticmethod
    def create_new_sell_order(price, amount, postonly):
        Util.get_logger().info("Placing Sell Order for " + str(amount) + " contracts at " + str(price))
        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)
        order = client.sell(ConfigManager.get_config().tradeInsturment, amount, price, postonly, "")
        return order

    @staticmethod
    def setup_inital_ladder():
        Util.get_logger().info("Setup initial ladder")

        for x in range(ConfigManager.get_config().numOfOrders):
            order = TradeManager.create_new_buy_order((ConfigManager.get_config().basePrice - ConfigManager.get_config().priceDistance) - (ConfigManager.get_config().priceDistance * x)
                , ConfigManager.get_config().contractSize, True)

            DatabaseManager.create_order_entry(order['order']['orderId'], order['order']['price'],order['order']['amount'], order['order']['direction'])

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
    def update_order_status():

        orders = DatabaseManager.get_all_open_orders()

        client = RestClient(ConfigManager.get_config().apiKey1, ConfigManager.get_config().apiSecret1, ConfigManager.get_config().apiUrl)

        Util.get_logger().info("Updating orders")

        for order in orders:

            updatedOrder = client.getorderstate(order.orderId)

            if updatedOrder['state'] == "filled":

                if updatedOrder['direction'] == "buy":

                    if ConfigManager.get_config().fcbMode:

                        #Create new one
                        newOrder = TradeManager.create_new_sell_order(updatedOrder["price"] + ConfigManager.get_config().priceDistance, updatedOrder['quantity'], False)
                        DatabaseManager.create_order_entry(newOrder['order']['orderId'], newOrder['order']['price'],newOrder['order']['quantity'], newOrder['order']['direction'])

                    else:

                        sellPriceOffset = ConfigManager.get_config().basePrice - updatedOrder["price"] 

                        #Create new one
                        newOrder = TradeManager.create_new_sell_order(ConfigManager.get_config().basePrice + sellPriceOffset, updatedOrder['quantity'], False)
                        DatabaseManager.create_order_entry(newOrder['order']['orderId'], newOrder['order']['price'],newOrder['order']['quantity'], newOrder['order']['direction'])

                else:

                    if ConfigManager.get_config().fcbMode:

                        newOrder = TradeManager.create_new_buy_order(updatedOrder["price"] - ConfigManager.get_config().priceDistance, updatedOrder['quantity'], False)
                        DatabaseManager.create_order_entry(newOrder['order']['orderId'], newOrder['order']['price'],newOrder['order']['quantity'], newOrder['order']['direction'])
                    else:
                        # put in buy order
                        buyPriceOffset = updatedOrder["price"] - ConfigManager.get_config().basePrice
                        #Create new one
                        newOrder = TradeManager.create_new_buy_order(ConfigManager.get_config().basePrice + buyPriceOffset, updatedOrder['quantity'], False)
                        DatabaseManager.create_order_entry(newOrder['order']['orderId'], newOrder['order']['price'],newOrder['order']['quantity'], newOrder['order']['direction'])

                DatabaseManager.update_order_entry(order.orderId, updatedOrder['state'])
