import datetime
import time

from bcolors import ConsoleColors

from src.connect import BitConnect


# Class to encapsulate the different trading algorithms
# Includes a function that simulates the ethereum market price (not accurately) and tests
# the algorithm on that
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
        switch_bound = float(t_data[0]["eth_usd"])
        holding = True
        starting_value = switch_bound
        current_value = float(self.connect.get_market_price('eth', 'usd'))
        new_file = open(str(datetime.datetime.utcnow()) + ".txt", "w+")
        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(2)

            # Current value of eth
            percent_change = ((1 - starting_value / current_value) * 100)

            # Print timestamp
            print ConsoleColors.OKBLUE + str(datetime.datetime.utcnow()) + " || %^:" + str(round(percent_change)) \
                  + " || ETH:" + str(current_value) + " || Switch Bound:" + str(switch_bound) + "|| Holding = " \
                  + str(holding) + ConsoleColors.ENDC
            new_file.write(str(datetime.datetime.utcnow()) + " || %^:" + str(round(percent_change)) \
                           + " || ETH:" + str(current_value) + " || Switch Bound:" + str(
                switch_bound) + "|| Holding = " + str(holding) + '\n')

            # Simulate value change
            if increasing:
                current_value += 2
            else:
                current_value -= 2

            if current_value < 220:
                increasing = True
            elif current_value > 320:
                increasing = False

            # If the current value reaches the Switch Bound and you are holding money
            if current_value <= switch_bound and holding:
                self.log += "Switch Bound Reached, Selling Moving Balance" + '\n'
                print ConsoleColors.WARNING + "Switch Bound Reached, Selling Moving Balance" + ConsoleColors.ENDC
                holding = False
                # Make sure you don't get stuck in a loop when the current value doesn't change
                switch_bound += switch_bound * .01

            # If the current value reaches the Switch Bound and you are not holding money
            elif current_value >= switch_bound and not holding:
                self.log += "Switch Bound Reached, Buying Moving Balance" + '\n'
                print ConsoleColors.WARNING + "Switch Bound Reached, Buying Moving Balance" + ConsoleColors.ENDC
                holding = True
                # Make sure you don't get stuck in a loop when the current value doesn't change
                switch_bound -= switch_bound * .01

            # If percent change increases to > interval then increase the Switch Bound by the interval bound change
            if percent_change > self.interval:
                new_bound = switch_bound + switch_bound * self.interval_bound_change
                self.log += "Raising ETH Switch Bound by " + str(self.interval_bound_change) + "% from " + str(
                    switch_bound) \
                            + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += str(datetime.datetime.utcnow())
                print ConsoleColors.WARNING + "Raising ETH Switch Bound by by " + str(
                    self.interval_bound_change) + "% from " \
                      + str(switch_bound) + " to " + str(new_bound) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

            # If the percent change decreases to < interval then decrease the Switch Bound by the interval bound change
            if percent_change < (self.interval * -1):
                new_bound = switch_bound - switch_bound * self.interval_bound_change
                self.log += "Lowering ETH Switch Bound by " + str(self.interval_bound_change) \
                            + "% from " + str(switch_bound) \
                            + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print ConsoleColors.WARNING + "Lowering ETH Switch Bound by " + str(self.interval_bound_change) \
                      + "% from " + str(switch_bound) + " to " + str(new_bound) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

    # Full working algorithm. Actually trades money in real time
    def full_wrench(self, add_avaliable_funds):
        # Runs the script until program quits
        t_data = self.connect.retrieve_transaction_history()
        current_value = float(self.connect.get_market_price('eth', 'usd'))
        try:
            switch_bound = float(t_data[0]["eth_usd"])
        except:
            switch_bound = current_value

        try:
            eth_balance = float(self.connect.get_account_balance('eth', 'usd')['eth_balance'])
        except:
            eth_balance = float(input("Authorization Failed. Enter Your Current ETH Balance Manually:"))

        try:
            usd_balance = float(self.connect.get_account_balance('eth', 'usd')['usd_balance'])
        except:
            usd_balance = float(input("Authorization Failed. Enter Your Current USD Balance Manually:"))

        # Ethereum eth_balance that will be moved with this algorithm (in ETH)

        starting_value = switch_bound

        # Determines if you are currently holding any eth
        if eth_balance > 0:
            moving_balance = eth_balance / 100
            holding = True
        else:
            moving_balance = usd_balance / 100
            holding = False

        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(3)
            # Current value of eth
            current_value = float(self.connect.get_market_price('eth', 'usd'))
            percent_change = (1 - starting_value / current_value) * 100
            # Print timestamp
            print str(datetime.datetime.utcnow())

            new_file = open(str(datetime.datetime.utcnow()) + ".txt", "w+")
            print ConsoleColors.OKBLUE + str(datetime.datetime.utcnow()) + " || %^:" + str(round(percent_change)) \
                  + " || ETH:" + str(current_value) + " || Switch Bound:" + str(switch_bound) + "|| Holding = " \
                  + str(holding) + ConsoleColors.ENDC
            new_file.write(str(datetime.datetime.utcnow()) + " || %^:" + str(round(percent_change)) \
                           + " || ETH:" + str(current_value) + " || Switch Bound:" + str(
                switch_bound) + "|| Holding = " + str(holding) + '\n')

            # If the current value reaches the switch_bound and you are holding money
            if current_value <= switch_bound and holding:
                #self.connect.cancel_orders()
                self.log += "Switch Bound Reached, Selling Moving Balance" + '\n'
                print("Switch Bound Reached, Selling Moving Balance")
                print(self.connect.market_sell(moving_balance, 'eth', 'usd')) + ConsoleColors.WARNING
                holding = False
                # Make sure you don't get stuck in a loop when the current value doesn't change
                switch_bound += switch_bound * .01

            # If the current value reaches the  switch_bound and you are not holding money
            elif current_value >= switch_bound and not holding:
                # On a buy order see if you can buy more since the current value is lower
                addi_val = 0
                # if eth_balance > 0 and add_avaliable_funds:
                #     addi_val = .1 * usd_balance / current_value
                # else:
                #     addi_val = 0
                #self.connect.cancel_orders()
                self.log += "Switch Bound Reached, Buying Moving Balance" + '\n'
                print("Switch Bound Reached, Buying Moving Balance")
                print ConsoleColors.WARNING + self.connect.market_buy(moving_balance + addi_val, 'eth',
                                                                      'usd') + ConsoleColors.ENDC
                holding = True
                # Make sure you don't get stuck in a loop when the current value doesn't change
                switch_bound -= switch_bound * .01

            # If percent change increases to > interval then increase the Switch Bound by the interval bound change
            if percent_change > self.interval:
                new_bound = switch_bound + switch_bound * self.interval_bound_change
                self.log += "Raising ETH Switch Bound by " + str(self.interval_bound_change) + "% from " \
                            + str(switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += datetime.datetime.utcnow()
                print ConsoleColors.WARNING + "Raising ETH Switch Bound by " + str(
                    self.interval_bound_change + "%from " + str(switch_bound)
                    + " to " + str(new_bound)) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

            # If the percent change decreases to < interval then decrease the Switch Bound by the interval bound change
            elif percent_change < (self.interval * -1):
                new_bound = switch_bound - switch_bound * self.interval_bound_change
                self.log += "Lowering ETH Switch Bound by " + str(self.interval_bound_change) + "% from " + str(
                    switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print ConsoleColors.WARNING + (
                "Lowering ETH Switch Bound by " + str(self.interval_bound_change) + "% from "
                + str(switch_bound) + " to " + str(new_bound)) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound


if __name__ == '__main__':

    algo = EthereumAlgorithms(5, .025, key, secret, customer_id)
    algo.test_wrench(False)
    # algo.full_wrench(False)
    # connect = BitConnect(key, secret, customer_id)
    # print connect.get_account_balance('eth', 'usd')
