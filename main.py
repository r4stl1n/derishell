import cmd
import time
import collections

from derishell.util.deribit_api import RestClient

from derishell.util.Util import Util
from derishell.managers.TradeManager import TradeManager
from derishell.managers.ConfigManager import ConfigManager
from derishell.managers.DatabaseManager import DatabaseManager
from derishell.util.RepeatedTimer import RepeatedTimer


class DeriShell(cmd.Cmd):

    prompt = 'DeriShell> '
    file = None
    rt = None

    def close(self):
        Util.get_logger().debug("Shutting Down")
        exit()

    def preloop(self):
        self.do_initalize("")

    def do_initalize(self, line):
        try:
            self.client2 = RestClient(ConfigManager.get_config().apiKey2, ConfigManager.get_config().apiSecret2, ConfigManager.get_config().apiUrl)
            self.client2.account()
            Util.get_logger().info("Credentials Verified")
        except:
            Util.get_logger().info("Api credentials invalid")
            self.close()

    def do_set_base_price(self, line):

        arguments = Util.safe_str_split_on_space(line)

        if len(arguments) >= 1:
            config = ConfigManager.get_config()
            config.basePrice = float(arguments[0])
            ConfigManager.update_config(config)
            Util.get_logger().info("Updated base price to: " + str(config.basePrice))
        else:
            Util.get_logger().info("Not enough parameters. Ex. set_base_price 6000")

    def do_set_num_orders(self, line):
        arguments = Util.safe_str_split_on_space(line)

        if len(arguments) >= 1:
            config = ConfigManager.get_config()
            config.numOfOrders = int(arguments[0])
            ConfigManager.update_config(config)
            Util.get_logger().info("Updated number of orders to: " + str(config.numOfOrders))
        else:
            Util.get_logger().info("Not enough parameters. Ex. set_num_orders 5")

    def do_set_contract_amount(self, line):

        arguments = Util.safe_str_split_on_space(line)

        if len(arguments) >= 1:
            config = ConfigManager.get_config()
            config.contractSize = int(arguments[0])
            ConfigManager.update_config(config)
            Util.get_logger().info("Updated number of contracts to: " + str(config.contractSize))
        else:
            Util.get_logger().info("Not enough parameters. Ex. set_contract_amount 100")       

    def do_set_price_distance(self, line):

        arguments = Util.safe_str_split_on_space(line)

        if len(arguments) >= 1:
            config = ConfigManager.get_config()
            config.priceDistance = float(arguments[0])
            ConfigManager.update_config(config)
            Util.get_logger().info("Updated price difference to: " + str(config.priceDistance))
        else:
            Util.get_logger().info("Not enough parameters. Ex. set_price_distance 1(in USD)")    

    def do_set_sl_price(self, line):

        arguments = Util.safe_str_split_on_space(line)

        if len(arguments) >= 1:
            config = ConfigManager.get_config()
            config.stopLossPrice = float(arguments[0])
            ConfigManager.update_config(config)
            Util.get_logger().info("Updated Stop Loss Price to: " + str(config.priceDistance))
        else:
            Util.get_logger().info("Not enough parameters. Ex. set_sl_price 6000(in USD)")    

    def do_check_accounts(self, line):
        if self.client2 != None:
            print(self.client2.account())

    def do_check_positions(self, line):
        if self.client2 != None:
            print(self.client2.positions())

    def do_get_summary(self,line):
        if self.client2 != None:
            print(self.client2.getsummary(ConfigManager.get_config().tradeInsturment))

    def do_test(self, line):
        if self.client2 != None:
            data = self.client2.buy(ConfigManager.get_config().tradeInsturment, 100, 9909, True, "")
            print(data)
            time.sleep(4)
            print(self.client2.orderhistory(10))    #currency is required for this function
            print(self.client2.getopenorders(ConfigManager.get_config().tradeInsturment, data['order']['orderId']))     #currency argument is optional. orderId to be removed

    def do_create_ladder(self, line):
        if self.client2 != None:
            TradeManager.setup_inital_ladder()

    def do_reset(self, line):

        if self.rt:
            self.rt.stop()
        
        TradeManager.cancel_all_current_orders()
        TradeManager.close_all_positions()
        TradeManager.stopLossTriggered = False
        DatabaseManager.delete_all_order_models()

        Util.get_logger().info("Derishell Reset")

    def do_cancel_orders(self, line):
        TradeManager.cancel_all_current_orders()

    def do_close_positions(self, line):
        TradeManager.close_all_positions()

    def do_pause(self, line):
        self.rt.stop()

    def do_start_update(self,line):
        if self.client2 != None:
            if self.rt == None:
                self.rt = RepeatedTimer(10, TradeManager.update_all)
            else:
                self.rt.start()

    def do_single_update(self, line):
        TradeManager.update_all()  

    def do_update_orders(self, line):
        if self.client2 != None:
            TradeManager.update_order_status()

    def do_show_orders(self, line):
        TradeManager.show_current_orders()

    def do_clear(self, line):
        Util.clear_screen()

    def do_quit(self, line):
        self.close()
        return True

    def do_exit(self, line):
        self.close()
        return True

if __name__ == '__main__':
    Util.clear_screen()
    print(Util.banner)
    DatabaseManager.initalize()
    DeriShell().cmdloop()
