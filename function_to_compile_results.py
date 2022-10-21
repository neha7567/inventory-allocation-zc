import numpy as np


def get_car_load_mean_variance(set_cars, start_date, end_date):
    utilization_dict = {key: set_cars[key].get_hours_booked() for key in set_cars.keys()}
    car_load_mean = sum(utilization_dict.values()) / len(utilization_dict.keys())
    car_load_var = 0
    for key in set_cars.keys():
        car_load_var += (utilization_dict[key] - car_load_mean) ** 2
    return car_load_mean, np.sqrt(car_load_var)


def get_average_pickup_distance_mean_var(allocation_rec, dist_mat):
    total_dist, var_dist = 0, 0
    for record in allocation_rec:
        total_dist += dist_mat[record[0] - 1, record[1] - 1]
    mean_dist = total_dist / len(allocation_rec)

    for record in allocation_rec:
        var_dist += (dist_mat[record[0], record[1]] - mean_dist) ** 2
    return mean_dist, np.sqrt(var_dist)


def frac_revenue_lost_in_empty_searches(empty_dic, total_inquiry_hours):
    rev = 0
    for key in empty_dic.keys():
        rev += empty_dic[key].bookingLength
    return rev / total_inquiry_hours


def mean_var_of_dict_vals(dictionary_input):
    arr = np.array(list(dictionary_input.values()))
    return [np.mean(arr), np.std(arr)]


def get_demand_profile_for_the_day(inquiry_object_dict):
    lead_time_list, booking_length_list = [], []
    for b_id in inquiry_object_dict.keys():
        lead_time_list.append(inquiry_object_dict[b_id].leadTime)
        booking_length_list.append(inquiry_object_dict[b_id].bookingLength)
    lead_arr, bl_arr = np.array(lead_time_list), np.array(booking_length_list)
    return [[np.mean(lead_arr), np.std(lead_arr)], [np.mean(bl_arr), np.std(bl_arr)]]


def get_summary_stats_results(set_cars, start_date, end_date, allocation_rec, dist_mat,
                              empty_search_dict, initial_age, total_booked_hours, total_hours_inquiries):
    dist_travelled_cars = {key: set_cars[key].age - initial_age[key] for key in set_cars.keys()}
    total_bookings = len(allocation_rec)
    num_empty_searches = len(empty_search_dict.keys())
    frac_rev_lost = frac_revenue_lost_in_empty_searches(empty_search_dict, total_hours_inquiries)
    mean_pickup_distance, variance_pickup_distance = get_average_pickup_distance_mean_var(allocation_rec, dist_mat)
    car_load_mean, car_load_var = get_car_load_mean_variance(set_cars, start_date, end_date)
    return total_bookings, num_empty_searches, [mean_pickup_distance, variance_pickup_distance], \
           [car_load_mean, car_load_var], mean_var_of_dict_vals(dist_travelled_cars), \
           frac_rev_lost, total_booked_hours / total_hours_inquiries


"""def get_average_earnings_per_agent(allBookings, AllocationRecord, weekend_number, s_o, s_u):
    revenue_weekday = 0
    revenue_weekend = 0

    for record in AllocationRecord:
        if allBookings[record[0]].startTime.weekday() in weekend_number:
            revenue_weekend += allBookings[record[0]].exPrice
        else:
            revenue_weekday += allBookings[record[0]].exPrice
    if s_o > 0:
        average_earning_per_opportunist = (revenue_weekday / (s_o) + revenue_weekend / (s_o + s_u))
        average_earning_per_utilitarian = revenue_weekend / ((s_o + s_u))
    else:
        average_earning_per_opportunist = 0
        average_earning_per_utilitarian = revenue_weekend / ((s_o + s_u))
    return average_earning_per_opportunist, average_earning_per_utilitarian


def optimal_var_values_to_alloc_rec(var_values):
    allocation_record = []
    for k in var_values:
        nameOfVariable = k[0]
        # print('nameOfVariable = '+ str(nameOfVariable))
        digitsincar = len(nameOfVariable) - nameOfVariable.find('_', 2) - 1
        # print('digitsincar =' + str(digitsincar))
        digits_in_booking = len(nameOfVariable) - (3 + digitsincar)
        # print('digitsinbooking =' + str(digitsinbooking))
        bookingNumber = int(nameOfVariable[2:2 + digits_in_booking])
        # print('bookingNumber ='+ str(bookingNumber))
        carNumber = int(nameOfVariable[digits_in_booking + 3:len(nameOfVariable)])
        # print('carNumber ='+str(carNumber))
        allocation_record.append((bookingNumber, carNumber))
        # print('allocationrecordfromgurobi='+ str(allocation_record))
    return allocation_record"""
