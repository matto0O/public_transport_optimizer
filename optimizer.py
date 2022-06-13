from scipy import optimize


def ticket_price_to_ride_time_ratio(time=20, normal=True, min_trip_length=0, max_trip_length=18):
    def time_to_price_radio(x):
        if x < 15:
            price = 1.6
        elif x < 30:
            price = 2.0
        else:
            price = 2.3
        if normal:
            price *= 2
        return price / x

    def lower_time_constraint(x):
        return x - min_trip_length

    def upper_time_constraint(x):
        return max_trip_length - x

    constraints = [{'type': 'ineq', 'fun': lower_time_constraint},
                   {'type': 'ineq', 'fun': upper_time_constraint}]

    return f"Best value for money is represented when traveling for " \
           f"{round(optimize.minimize(time_to_price_radio, x0=time, constraints=constraints).x[0])} minutes"
