from connect import BitConnect
import time
import datetime


def run_script():
    connect = BitConnect(key, secret, customer_id)
    # Runs the script until program quits
    log = ""
    t_data = connect.retrieve_transaction_history()
    eth_lower_bound = float(t_data[0]["eth_usd"])
    # eth_balance = connect.get_account_balance('eth', 'usd')['eth_balance']
    # Ethereum eth_balance that will be moved with this algorithm (in ETH)
    # moving_balance = connect.get_account_balance('eth', 'usd')['eth_balance']
    # Determines if you are currently holding any eth
    # if eth_balance > 0:
    #     holding = True
    # else:
    #     holding = False

    # Test Values
    moving_balance = .05
    holding = True

    while True:
        # Make the system sleep to prevent API overuse
        time.sleep(3)
        # Current value of eth
        current_value = float(connect.get_market_price('eth', 'usd'))
        # Print timestamp
        print str(datetime.datetime.utcnow())

        # If the current value reaches the lower bound and you are holding money
        if current_value <= eth_lower_bound and holding:
            #connect.cancel_orders()
            log += "Lower Bound Reached, Selling Moving Balance" + '\n'
            print("Lower Bound Reached, Selling Moving Balance")
            # print(connect.market_sell(moving_balance, 'eth', 'usd'))
            holding = False
            # Make sure you don't get stuck in a loop when the current value doesn't change
            eth_lower_bound += eth_lower_bound * .01

        # If the current value reaches the lower bound and you are not holding money
        elif current_value >= eth_lower_bound and not holding:
            addi_val = 0
            # On a buy order see if you can buy more since the current value is lower
            # if eth_balance["usd_balance"] > 0:
            #     addi_val = .1 * eth_balance["usd_balance"] / current_value
            # else:
            #     addi_val = 0

            #connect.cancel_orders()
            log += "Lower Bound Reached, Buying Moving Balance" + '\n'
            print("Lower Bound Reached, Buying Moving Balance")
            # print(connect.market_buy(moving_balance + addi_val,'eth', 'usd'))
            holding = True
            # Make sure you don't get stuck in a loop when the current value doesn't change
            eth_lower_bound -= eth_lower_bound * .01

        # If the percent change increases by more than 5% then increase the lower bound by 2.5%
        if connect.get_percent_change('eth', 'usd') > 5:
            new_bound = eth_lower_bound + eth_lower_bound * .25
            log += "Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current Value is at " + str(current_value) + '\n'
            log += datetime.datetime.utcnow()
            print("Raising ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound))
            print("Current Value is at " + str(current_value))
            eth_lower_bound = new_bound

        # If the percent change decreases by more than 5% then decrease the lower bound by 2.5%
        if connect.get_percent_change('eth', 'usd') < -5:
            new_bound = eth_lower_bound - eth_lower_bound * .25
            log += "Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound) + '\n'
            log += "Current ETH Value is at " + str(current_value) + '\n'
            print("Lowering ETH Lower Bound by 5% from" + str(eth_lower_bound) + " to " + str(new_bound))
            print("Current ETH Value is at " + str(current_value))
            eth_lower_bound = new_bound


if __name__ == '__main__':
    run_script()












