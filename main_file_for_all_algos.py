import generate_demand_supply
import input_paramteres
import input_demand_data
import legacy_allocation_functions as legacy
import MIP_algo_allocation_functions as MIP
import function_to_compile_results as compile_res
import pandas as pd
import scipy.stats
import numpy as np


def total_inquiry_hours(inq_dict):
    hrs = 0
    for i in inq_dict.keys():
        hrs += inq_dict[i].bookingLength
    return hrs


def data_from_results_dict(res_dict, algo, date_start, inquiry_profile):
    QTY = ['Total Booked', 'Number empty searches', 'Mean pickup distance', 'Mean car loads',
           'Mean_distance_load',
           'Frac_Revenue_lost_in_empty_search',
           'Frac_Revenue_earned']
    data_res = pd.DataFrame.from_dict(res_dict)
    data_res.columns = ['Metric_values']
    data_res['Metrics'] = QTY
    data_res['Date'] = date_start
    data_res['Algorithm'] = algo
    data_res['Mean_lead_Time'], data_res['std_lead_Time'] = inquiry_profile[0][0], inquiry_profile[0][1]
    data_res['Mean_booking_Time'], data_res['std_booking_Time'] = inquiry_profile[1][0], inquiry_profile[1][1]
    return data_res


def get_results_for_given_date(filename):
    demand_csv_file_path, demand_pkl_file_path = filename + '.csv', filename + '.p'
    demand_data = input_demand_data.get_demand_data(demand_csv_file_path, demand_pkl_file_path)

    all_inquiry_dict, sorted_inquiry_list = generate_demand_supply.gen_inquiries_from_real_data(demand_data)
    distance_matrix = generate_demand_supply.generate_distance_matrix_car_inquiry(all_inquiry_dict,
                                                                                  input_paramteres.num_cars)
    is_converted_list = scipy.stats.bernoulli.rvs(input_paramteres.conversion_probability,
                                                  size=len(sorted_inquiry_list),
                                                  random_state=12)

    is_converted_dict = {i: is_converted_list[i] for i in all_inquiry_dict.keys()}
    startDate, endDate = min(demand_data.time_stamp), max(demand_data.time_stamp)
    inquiries_profile = compile_res.get_demand_profile_for_the_day(all_inquiry_dict)

    functions = [('legacy_no_reshuffle', legacy.get_legacy_revenue_without_waiting),
                 ('legacy_reshuffle', legacy.get_legacy_revenue_with_reshuffling), 
                 ('MIP_no_wait', MIP.MIP_no_wait), ('MIP_wait', MIP.MIP_with_wait)]
    # functions = [('MIP_no_wait', MIP.MIP_no_wait), ('MIP_wait', MIP.MIP_with_wait)]

    result_df_for_a_day = pd.DataFrame()
    for rec in functions:
        results_dict = {}
        gen_set_cars = generate_demand_supply.generate_cars(input_paramteres.num_cars, input_paramteres.car_group)
        start_age = {key: gen_set_cars[key].age for key in gen_set_cars.keys()}

        set_cars, allocation_record, empty_searches, total_rev = \
            rec[1](sorted_inquiry_list, gen_set_cars, is_converted_dict)
        results_dict[rec[0]] = compile_res.get_summary_stats_results(set_cars, startDate, endDate, allocation_record,
                                                                     distance_matrix, empty_searches, start_age,
                                                                     total_rev, total_inquiry_hours(all_inquiry_dict))
        result_df_for_a_day = result_df_for_a_day.append(data_from_results_dict(results_dict, rec[0], startDate,
                                                                                inquiries_profile),
                                                         ignore_index=True)
    return result_df_for_a_day


path_file = 'G:\\My Drive\\ZoomCar_data\\applied_analytics_data\\researchdata\\'
files = [i.strftime("%d-%b-%Y") for i in pd.date_range(start="2021-12-03", end="2021-12-15")]

result_df_list = pd.DataFrame()

for file_name in files:
    result_df_list = result_df_list.append(get_results_for_given_date(path_file + file_name + '-Search_Data'))
    result_df_list.to_csv(path_file + file_name + "_Results.csv")
# pd.concat(result_df_list, axis=0).to_csv(path_file + 'results.csv', sep=',')

print(result_df_list)
