import datetime
import time
from bcolors import ConsoleColors
from src.connect import BitConnect
import json


# Class to encapsulate the different trading algorithms
# Includes a function that simulates the Ethereum market price (not accurately) and tests
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
        starting_time = str(datetime.datetime.utcnow())
        new_file = open("log-" + starting_time + ".txt", "w+")
        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(1)

            # Current value of eth
            percent_change = ((1 - starting_value / current_value) * 100)

            # Print timestamp
            print ConsoleColors.OKBLUE + str(datetime.datetime.utcnow()) + " || %^:" + str(round(percent_change)) \
                  + " || ETH:" + str(current_value) + " || Switch Bound:" + str(switch_bound) + "|| Holding = " \
                  + str(holding) + ConsoleColors.ENDC

            log_object = {
                "time": str(datetime.datetime.utcnow()),
                "percent_change": str(round(percent_change)),
                "eth_value": str(current_value),
                "switch_bound": str(switch_bound),
                "holding": str(holding)}

            new_file.write(json.dumps(log_object) + "\n")

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
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                self.log += "Raising ETH Switch Bound by " + str(self.interval_bound_change) + "% from " \
                            + str(switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += str(datetime.datetime.utcnow())
                print ConsoleColors.WARNING \
                      + "Raising ETH Switch Bound by " + str((percent_change * self.interval_bound_change)) \
                      + " % from " + str(switch_bound) \
                      + " to " + str(new_bound) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

            # If the percent change decreases to < interval then decrease the Switch Bound by the interval bound change
            if percent_change < (self.interval * -1):
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                self.log += "Lowering ETH Switch Bound by " + str(self.interval_bound_change) + "% from " + str(
                    switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print ConsoleColors.WARNING + (
                    "Lowering ETH Switch Bound by " + str(
                        (percent_change * self.interval_bound_change)) + "% from "
                    + str(switch_bound) + " to " + str(new_bound)) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

    # Full working algorithm. Actually trades money in real time
    def full_wrench(self, add_avaliable_funds):
        # Runs the script until program quits
        t_data = self.connect.retrieve_transaction_history()
        current_value = float(self.connect.get_market_price('eth', 'usd'))
        num_of_calls = 1
        try:
            switch_bound = float(t_data[0]["eth_usd"])
        except:
            switch_bound = current_value

        try:
            eth_balance = round(float(self.connect.get_account_balance('eth', 'usd')['eth_balance']), 6)
            num_of_calls += 1
        except:
            eth_balance = round(float(input("Authorization Failed. Enter Your Current ETH Balance Manually:")), 6)

        try:
            usd_balance = round(float(self.connect.get_account_balance('eth', 'usd')['usd_balance']), 6)
            num_of_calls += 1
        except:
            usd_balance = round(float(input("Authorization Failed. Enter Your Current USD Balance Manually:")), 6)

        # Ethereum eth_balance that will be moved with this algorithm (in ETH)
        starting_value = switch_bound

        # Determines if you are currently holding any eth
        if eth_balance > 0:
            moving_balance = eth_balance
            holding = True
        else:
            moving_balance = usd_balance / current_value
            holding = False

        # TODO: ADD TRANSACTION FEE

        starting_time = str(datetime.datetime.utcnow())
        new_file = open("log-" + starting_time + ".txt", "w+")



        while True:
            # Make the system sleep to prevent API overuse
            time.sleep(4)
            # Current value of eth
            try:
                current_value = float(self.connect.get_market_price('eth', 'usd'))
                num_of_calls += 1
            except:
                current_value = current_value

            percent_change = (1 - starting_value / current_value) * 100
            # Print Info

            print ConsoleColors.OKBLUE + str(datetime.datetime.utcnow()) + "\t|| %^:" + str(round(percent_change)) \
                  + "\t|| ETH:" + str(round(current_value, 2)) + "\t|| Switch Bound:" + str(
                round(switch_bound, 2)) + "\t|| ETH Balance:" \
                  + str(round(eth_balance, 2)) + "\t|| USD Balance:" + str(
                round(usd_balance, 2)) + "\t|| Moving Balance:" \
                  + str(moving_balance) + "\t|| API Calls:" \
                  + str(num_of_calls) + "\t|| Holding = " \
                  + str(holding) + ConsoleColors.ENDC

            # Log Info
            log_object = {
                "time": str(datetime.datetime.utcnow()),
                "percent_change": str(round(percent_change)),
                "eth_value": str(current_value),
                "switch_bound": str(switch_bound),
                "eth_balance": str(eth_balance),
                "usd_balance": str(usd_balance),
                "holding": str(holding),
                "api_calls": str(num_of_calls),
                "moving_balance": str(moving_balance)}

            new_file.write(json.dumps(log_object) + "\n")

            # If the current value reaches the switch_bound and you are holding money
            if current_value <= switch_bound and holding:
                # Cancel existing orders and then sell
                # self.connect.cancel_orders()
                # num_of_calls += 1
                self.log += "Switch Bound Reached, Selling Moving Balance" + '\n'
                print ConsoleColors.WARNING + "Switch Bound Reached, Selling Moving Balance" + ConsoleColors.ENDC
                # print ConsoleColors.WARNING +
                # json.dumps(self.connect.market_sell(round(moving_balance, 6), 'eth', 'usd')) + ConsoleColors.ENDC
                holding = False
                # Update USD and ETH Balance
                eth_balance -= moving_balance
                usd_balance += moving_balance * current_value
                moving_balance = usd_balance / current_value
                # Make sure you don't get stuck ina trade loop  when the current value doesn't change
                switch_bound += switch_bound * .001

            # If the current value reaches the  switch_bound and you are not holding money
            elif current_value >= switch_bound and not holding:
                # Cancel existing orders and then buy
                # self.connect.cancel_orders()
                # num_of_calls += 1
                self.log += "Switch Bound Reached, Buying Moving Balance" + '\n'
                print("Switch Bound Reached, Buying Moving Balance")
                moving_balance = usd_balance / current_value
                # print ConsoleColors.WARNING + json.dumps(self.connect.market_buy(round(moving_balance, 6), 'eth',
                #                                                       'usd')) + ConsoleColors.ENDC
                holding = True
                # Update USD and Ethereum Balance
                eth_balance += moving_balance
                usd_balance -= moving_balance * current_value
                # Make sure you don't get stuck in a trade loop when the current value doesn't change
                switch_bound -= switch_bound * .001

            # If percent change increases to > interval then increase the Switch Bound by the price increase * ibc
            if percent_change > self.interval:
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                self.log += "Raising ETH Switch Bound by " + str(self.interval_bound_change) + "% from " \
                            + str(switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current Value is at " + str(current_value) + '\n'
                self.log += str(datetime.datetime.utcnow())
                print ConsoleColors.WARNING \
                      + "Raising ETH Switch Bound by " + str((percent_change * self.interval_bound_change)) \
                      + " % from " + str(switch_bound) \
                      + " to " + str(new_bound) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound

            # If the percent change decreases to < interval then decrease the Switch Bound by the price increase * ibc
            elif percent_change < (self.interval * -1):
                new_bound = switch_bound + (switch_bound * ((percent_change / 100) * self.interval_bound_change))
                self.log += "Lowering ETH Switch Bound by " + str(self.interval_bound_change) + "% from " + str(
                    switch_bound) + " to " + str(new_bound) + '\n'
                self.log += "Current ETH Value is at " + str(current_value) + '\n'
                print ConsoleColors.WARNING + (
                    "Lowering ETH Switch Bound by " + str(
                        (percent_change * self.interval_bound_change)) + "% from "
                    + str(switch_bound) + " to " + str(new_bound)) + ConsoleColors.ENDC
                switch_bound = new_bound
                starting_value = switch_bound


if __name__ == '__main__':

    algo = EthereumAlgorithms(1, .85, key, secret, customer_id)
    # algo.test_wrench(False)
    algo.full_wrench(False)
