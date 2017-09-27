from connect import BitConnect
import time
import datetime
from bcolors import ConsoleColors


class EthereumAlgorithms:
    log = ""
    interval = 0
    interval_bound_change = 0
    connect = ()

    def __init__(self, interval, interval_bound_change, key, secret, customer_id):
        self.log = ""
        self.interval = interval
        self.interval_bound_change = interval_bound_change
        self.connect = BitConnect(key, secret, customer_id)

    # For testing purposes
    def test_wrench(self, increasing):
        # Runs the script until program quits
        t_data = self.connect.retrieve_transaction_history()
        eth_lower_bound = float(t_data[0]["eth_usd"])
        holding = True
        starting_value = eth_lower_bound
        current_value = float(self.connect.get_market_price('eth', 'usd'))

        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(2)
            # Current value of eth

            percent_change = (1 - starting_value / current_value) * 100

            # Print timestamp
            print ConsoleColors.OKBLUE + str(datetime.datetime.utcnow()) + " || %^:" + str(percent_change) \
                  + " || ETH:" + str(current_value) + " || Lower Bound:" + str(eth_lower_bound) + ConsoleColors.ENDC

            # Simulate value change
            if increasing:
                current_value += 2
            else:
                current_value -= 2

            # If the current value reaches the lower bound and you are holding money
            if current_value <= eth_lower_bound and holding:
                self.log += "Lower Bound Reached, Selling Moving Balance" + '\n'
                print ConsoleColors.WARNING + "Lower Bound Reached, Selling Moving Balance" + ConsoleColors.ENDC
                holding = False
                # Make sure you don't get stuck in a loop when the current value doesn't change
                eth_lower_bound += eth_lower_bound * .01

            # If the current value reaches the lower bound and you are not holding money
            elif current_value >= eth_lower_bound and not holding:
                self.log += "Lower Bound Reached, Buying Moving Balance" + '\n'
                print ConsoleColors.WARNING + "Lower Bound Reached, Buying Moving Balance" + ConsoleColors.ENDC
                holding = True
                # Make sure you don't get stuck in a loop when the current value doesn't change
                eth_lower_bound -= eth_lower_bound * .01

            # If the percent change increases by more than 5% then increase the lower bound by 2.5%
            if percent_change > self.interval:
                new_bound = eth_lower_bound + eth_lower_bound * self.interval_bound_change
                self.log += "Raising ETH Lower Bound by " + str(self.interval_bound_change) + "% from " + str(eth_lower_bound) \
                            + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += str(datetime.datetime.utcnow())
                print ConsoleColors.WARNING + "Raising ETH Lower Bound by by " + str(self.interval_bound_change) + "% from "\
                      + str(eth_lower_bound) + " to " + str(new_bound) + ConsoleColors.ENDC
                eth_lower_bound = new_bound
                starting_value = eth_lower_bound

            # If the percent change decreases by more than 5% then decrease the lower bound by 2.5%
            if percent_change < (self.interval * -1):
                new_bound = eth_lower_bound - eth_lower_bound * self.interval_bound_change
                self.log += "Lowering ETH Lower Bound by " + str(self.interval_bound_change)\
                            + "% from " + str(eth_lower_bound) \
                            + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print ConsoleColors.WARNING + "Lowering ETH Lower Bound by " + str(self.interval_bound_change)\
                      + "% from " + str(eth_lower_bound) + " to " + str(new_bound) + ConsoleColors.ENDC
                eth_lower_bound = new_bound
                starting_value = eth_lower_bound

    # Full working algorithm. Actually trades money in real time
    def full_wrench(self):
        # Runs the script until program quits
        t_data = self.connect.retrieve_transaction_history()
        eth_lower_bound = float(t_data[0]["eth_usd"])
        eth_balance = self.connect.get_account_balance('eth', 'usd')['eth_balance']
        usd_balance = self.connect.get_account_balance('eth', 'usd')['usd_balance']
        # Ethereum eth_balance that will be moved with this algorithm (in ETH)
        moving_balance = self.connect.get_account_balance('eth', 'usd')['eth_balance']
        starting_value = eth_lower_bound
        # Determines if you are currently holding any eth
        if eth_balance > 0:
            holding = True
        else:
            holding = False

        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(3)
            # Current value of eth
            current_value = float(self.connect.get_market_price('eth', 'usd'))
            percent_change =  (1 - starting_value / current_value) * 100
            # Print timestamp
            print str(datetime.datetime.utcnow())

            # If the current value reaches the lower bound and you are holding money
            if current_value <= eth_lower_bound and holding:
                self.connect.cancel_orders()
                self.log += "Lower Bound Reached, Selling Moving Balance" + '\n'
                print("Lower Bound Reached, Selling Moving Balance")
                print(self.connect.market_sell(moving_balance, 'eth', 'usd')) + ConsoleColors.WARNING
                holding = False
                # Make sure you don't get stuck in a loop when the current value doesn't change
                eth_lower_bound += eth_lower_bound * .01

            # If the current value reaches the lower bound and you are not holding money
            elif current_value >= eth_lower_bound and not holding:
                # On a buy order see if you can buy more since the current value is lower
                if eth_balance > 0:
                    addi_val = .1 * usd_balance / current_value
                else:
                    addi_val = 0

                self.connect.cancel_orders()
                self.log += "Lower Bound Reached, Buying Moving Balance" + '\n'
                print("Lower Bound Reached, Buying Moving Balance")
                print(self.connect.market_buy(moving_balance + addi_val, 'eth', 'usd')) + ConsoleColors.WARNING
                holding = True
                # Make sure you don't get stuck in a loop when the current value doesn't change
                eth_lower_bound -= eth_lower_bound * .01

            # If the percent change increases by more than 5% then increase the lower bound by 2.5%
            if percent_change > self.interval:
                new_bound = eth_lower_bound + eth_lower_bound * self.interval_bound_change
                self.log += "Raising ETH Lower Bound by " + str(self.interval_bound_change) + "% from " \
                            + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += datetime.datetime.utcnow()
                print("Raising ETH Lower Bound by " + str(self.interval_bound_change) + "%from " + str(eth_lower_bound)
                      + " to " + str(new_bound)) + ConsoleColors.WARNING
                eth_lower_bound = new_bound
                starting_value = eth_lower_bound

            # If the percent change decreases by more than 5% then decrease the lower bound by 2.5%
            if percent_change < (self.interval * -1):
                new_bound = eth_lower_bound - eth_lower_bound * self.interval_bound_change
                self.log += "Lowering ETH Lower Bound by " + str(self.interval_bound_change) + "% from " + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print("Lowering ETH Lower Bound by " + str(self.interval_bound_change) + "% from "
                      + str(eth_lower_bound) + " to " + str(new_bound)) + ConsoleColors.WARNING
                eth_lower_bound = new_bound
                starting_value = eth_lower_bound


if __name__ == '__main__':
    algo = EthereumAlgorithms(5, .025, key, secret, customer_id)
    algo.test_wrench(False)












