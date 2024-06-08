from uuid import uuid4
import random
import numpy as np
import csv
import json

class Driver:
    def __init__(self):
        self.id = uuid4()
        
    def does_churn(self):
        return random.random() <= 0.05       
        
    def __repr__(self):
        return f"Driver ({self.id})"
    
class Rider:
    def __init__(self):
        self.id = uuid4()
        self.has_failed_ride = False
        
    def fail_ride(self):
        self.has_failed_ride = True
        
    def does_churn(self):
        if self.has_failed_ride:
            return random.random() <= 0.10 # 10% monthly churn rate if failed rides
        else:
            return random.random() <= 0.33 # 33% monthly churn rate if no failed rides
        
    def __repr__(self):
        return f"Rider ({self.id}, {self.has_failed_ride})"

class Marketplace:
    def __init__(self):
        self.id = uuid4()
        # self.num_drivers = 0
        # self.num_riders = 0
        self.rider_cac_total = 0
        self.driver_cac_total = 0
        self.total_rider_payments = 0
        self.total_driver_payouts = 0
        self.drivers = []
        self.riders = []
        self.num_churned_drivers = 0
        self.num_churned_riders = 0
        self.total_successful_rides = 0
        self.total_failed_rides = 0
        
    def acquire_rider(self):
        self.riders.append(Rider())
        # self.rider_cac_total += 20
        self.rider_cac_total += self.compute_rider_cac()
        # self.num_riders += 1
    
    def acquire_driver(self):
        self.drivers.append(Driver())
        # self.driver_cac_total += 600
        self.driver_cac_total += self.compute_driver_cac()
        # self.num_drivers += 1
    
    def compute_rider_cac(self):
        # somewhere between $10 and $20
        # use a linear function y=mx+b for simplicity; cost will be $20 at max_num_riders, $10 for the first rider. 
        # m = (y2-y1) / (x2-x1)
        m = (20-10) / (max_num_riders - 0) # 0.05 at 200 riders per month max
        b = 10
        y = m * len(self.riders) + b
        return y
        
    def compute_driver_cac(self):
        # somewhere between $400 and $600, a function of the number of existing drivers
        # using linear function; cost will be $600 at max_num_drivers, $400 for first driver
        m = (600-400) / (max_num_drivers - 0)
        b = 10
        y = m * len(self.drivers) + b
        return y
        
    def churn_rider(self, rider):
        self.riders.remove(rider)
        self.num_churned_riders += 1
    
    def churn_driver(self, driver):
        self.drivers.remove(driver)
        self.num_churned_drivers += 1
        
    def __repr__(self):
        attributes = ', '.join([f"{key}={value!r}" for key, value in vars(self).items() if key not in ['drivers', 'riders', 'id']])
        return f"Lyft: {attributes})"

def rider_finds_driver(driver_pay):
    # this could be smarter; tried a logistic function to approximate s-curve, but can't get the parameters to match known points. 
    # Instead, will use a linear function
    
    # if it falls in the known range, use a linear function based on those two points. 
    if 19 >= driver_pay >= 22:
        m = (0.93-0.60) / (22-19) # 0.11
        b = -1.49
        y = m * driver_pay + b
        return random.random() <= y
    
    # if it's above $22, need to change the function to shallower line a la top of S-curve, because can't go over 100%, 
    # also assume that not all rides will be successful either because drivers don't feel it's enough 
    # or b/c logistical issues (bugs, driver not paying attention, etc.)
    elif driver_pay > 22:
        m = (0.97 - 0.93) / (24 - 22) # ASSUMPTION; $24 will raise by a further 4%; "curve" flattens off
        b = 0.49
        y = m * driver_pay + b
        return random.random() <= y
    
    # ASSUMPTION: $15 will drop to 30%; m=0.075; "curve" is shallower before going above prevailing wage
    # m=0.05 if $15 == 40% match
    # m=0.15 if $15 == 0% match
    elif driver_pay >= 15:
        m = (0.6 - 0.3) / (19 - 15) 
        b = -0.825
        y = m * driver_pay + b
        return random.random() <= y
        
    # ASSUMPTION that below a given price, especially below prevailing wage drivers just won't take the ride (will use Uber or another service)
    else: 
        return False

# doing core logic by month, since all the input figures (churn, rides/month) were given monthly
def simulate_month(lyft):
    # to begin a month, first simulate driver/rider acquisition
    # this also ensures there is at least one driver/rider in month 1
        
    # acquire drivers up to the max #
    # add to drivers list and bump driver cac total; the class does this
    if len(lyft.drivers) < max_num_drivers:
        # acquire at least 1 and up to 10% of the max_num_drivers
        num_drivers_to_acquire = int(max_num_drivers / 10)
        if num_drivers_to_acquire == 0:
            num_drivers_to_acquire = 1
        for i in range(num_drivers_to_acquire):
            lyft.acquire_driver()
        # another way to do this would be to acquire a consistent # or % of riders each month, up to the max. 
        
    # acquire riders up to the max #
    # add to riders list and bump rider cac total; the class handles this
    if len(lyft.riders) < max_num_riders:
        # acquire at least 1 and up to 10% of the max_num_riders
        num_riders_to_acquire = int(max_num_riders / 10)
        for i in range(num_riders_to_acquire):
            lyft.acquire_rider()
        
    # next, iterate through the list of riders in the marketplace
    for rider in lyft.riders:
        # simulate that rider trying to match for a ride (just 1, since that's the average per the prompt):
        ride_match = rider_finds_driver(driver_pay)

        # if ride is successful:
        if ride_match:
            # add $25 to lyft.total_rider_payments
            # add 25 - lyft_take to lyft.total_driver_payouts
            lyft.total_rider_payments += 25
            lyft.total_driver_payouts += driver_pay
            lyft.total_successful_rides += 1
        # if ride is not successful:
        else:
            # record that specific rider as having a failed ride.
            rider.fail_ride()
            lyft.total_failed_rides += 1
                
        # next, simulate if the rider churned (%s handled in the Rider class)
        # if rider.has_failed_ride:
            # 33% chance of churning
            # else: 10% chance of churning
        if rider.does_churn():
            lyft.churn_rider(rider)
            
    # finally, simulate driver churn; iterate through list of drivers and for each:
    for driver in lyft.drivers:
        # 5% chance of churning; handled in the Driver class
        if driver.does_churn():
            lyft.churn_driver(driver)       

# repeats the monthly simulation 12 times, and returns the cumulative results
def simulate_year():
    lyft = Marketplace()
    # print(lyft.id)

    # repeat 12 times
    for i in range(1, 13):
        simulate_month(lyft)
        # print(f"Month {i}: {repr(lyft)}")

    # finally, add up Lyft's net revenue:
    net_revenue = (lyft.total_rider_payments - lyft.total_driver_payouts - lyft.rider_cac_total - lyft.driver_cac_total)
    
    return {
        'net_revenue': net_revenue,
        'total_rider_payments': lyft.total_rider_payments,
        'total_driver_payouts': lyft.total_driver_payouts,
        'rider_cac_total': lyft.rider_cac_total,
        'driver_cac_total': lyft.driver_cac_total, 
        'num_churned_drivers': lyft.num_churned_drivers, 
        'num_churned_riders': lyft.num_churned_riders, 
        'num_successful_rides': lyft.total_successful_rides,
        'num_failed_rides': lyft.total_failed_rides
    }

NUM_YEARS_TO_SIMULATE = 100

lyft_take_scenarios = [0.5, 2, 4, 6, 8, 9, 10]
max_driver_rider_scenarios = [(5,100), (2,200), (5,200), (10,200), (10, 1000)] # the most drivers and riders in the marketplace

overall_simulation_results = []

# run the simulation NUM_YEARS_TO_SIMULATE times for each combination of lyft take and num drivers/riders. 
# average and return the results for each input combination. 
for driver_rider_scenario in max_driver_rider_scenarios:
    max_num_drivers, max_num_riders = driver_rider_scenario[0], driver_rider_scenario[1]
    # for each lyft_take_scenario:
    for lyft_take_scenario in lyft_take_scenarios:
        lyft_take = lyft_take_scenario
        rider_cost = 25
        driver_pay = (rider_cost - lyft_take)
    
        # simulate 1000 years to get an average net income with those parameters
        simulated_marketplace_years = []
        simulated_net_revenues = []

        for i in range(NUM_YEARS_TO_SIMULATE):
            simulation_results = simulate_year()
            simulated_marketplace_years.append(simulation_results)
            simulated_net_revenues.append(simulation_results['net_revenue'])   
                    
        # get the average for each value across all years
        sum_dict = {key: 0 for key in simulated_marketplace_years[0]}
        for year in simulated_marketplace_years:
            for key in year:
                sum_dict[key] += year[key] 
        averages = {key: value / NUM_YEARS_TO_SIMULATE for key, value in sum_dict.items()}
        
        # record the max number of drivers/riders, lyft take, and net revenue

        average_net_revenue = averages['net_revenue'] 
        
        print(f"\n\tDrivers: {max_num_drivers}\n\tRiders: {max_num_riders}\n\tLyft Take: {lyft_take}\n\t\tAverage net revenue: {averages['net_revenue']}\n")
        
        overall_simulation_results.append({
            "total_rider_payments": averages['total_rider_payments'],
            "total_driver_payouts": averages['total_driver_payouts'],
            "rider_cac_total": averages['rider_cac_total'],
            "driver_cac_total": averages['driver_cac_total'],
            "num_churned_drivers": averages['num_churned_drivers'],
            "num_churned_riders": averages['num_churned_riders'],
            "num_successful_rides": averages['num_successful_rides'],
            "num_failed_rides": averages['num_failed_rides'],
            'max_num_drivers': max_num_drivers,
            'max_num_riders': max_num_riders,
            'lyft_take': lyft_take,
            'net_revenue': average_net_revenue,
        })

# dump results to a CSV for charting and analysis
with open(f"simulation_results.csv", 'w', newline='') as file:
    fieldnames = overall_simulation_results[0].keys()
    csv_output = csv.DictWriter(file, fieldnames=fieldnames)
    csv_output.writeheader()
    csv_output.writerows(overall_simulation_results)
