import scipy.stats
import important_function_for_both_algos as imp_funcs
import copy
import input_paramteres

critical_hours = input_paramteres.critical_hours


def get_legacy_revenue_without_waiting(sortedInquiries, setCars, is_converted_dict):
    """
    This is the logic for ZC legacy algo.
    input :
        sortedInquiries - sorted by inquiry time, tuple of booking id and booking object
        setCars - dictionary, carkey and car schedule.
        startDate - startDate of the earliest Booking
        endDate - endi date of time horizon
        blocked_mins = given s_u utilitarian cars, block weekdays on all s_u cars.

    output : total revenue
            number of requests completed
            average asset utilization
            AllocationRecord - tuple of booking id and car id
    """
    empty_search_bookings = {}
    totalRevenue = 0
    AllocationRecord = []  # tuple of booking Id, car Id

    for y in sortedInquiries:
        eligible_car_ids = imp_funcs.get_eligible_carids_for_booking(y[1], setCars)
        carIdAllocated = imp_funcs.max_weight_algo_legacy(y[1], setCars, eligible_car_ids)
        is_converted = is_converted_dict[y[0]]
        if carIdAllocated is not None:
            if is_converted == 1:
                setCars[carIdAllocated].completeBooking(y[1])
                AllocationRecord.append((y[0], carIdAllocated))
                totalRevenue += y[1].bookingLength
        else:
            empty_search_bookings.update({y[0]: y[1]})

    return setCars, AllocationRecord, empty_search_bookings, totalRevenue


def get_legacy_revenue_with_reshuffling(sortedInquiries, setCars, is_converted_dict):
    totalRevenue = 0
    AllocationRecord = []  # tuple of booking Id, car Id
    empty_search_bookings, allocated_bookings_dict = {}, {}

    for y in sortedInquiries: # starting one by one with each inquiry
        eligible_car_ids = imp_funcs.get_eligible_carids_for_booking(y[1], setCars)
        if eligible_car_ids:
            if is_converted_dict[y[0]] == 1:
                carIdAllocated = imp_funcs.max_weight_algo_legacy(y[1], setCars, eligible_car_ids)
                setCars[carIdAllocated].completeBooking(y[1])  # only block and don't change car age.
                AllocationRecord.append((y[0], carIdAllocated))
                allocated_bookings_dict.update({y[0]: y[1]})
        else: # reshuffle and check if there is really no space for this
            bookings_can_be_reshuffled_dict, hard_coded_allocation_rec = \
                imp_funcs.get_reshuffleable_bookings_and_hardbooked_allocation_record(AllocationRecord,
                                                                                      allocated_bookings_dict,
                                                                                      y[1].inquiryTime, critical_hours)
            setCars = imp_funcs.remove_reshuffable_bookings_from_car(setCars, AllocationRecord,
                                                                     bookings_can_be_reshuffled_dict)
            bookings_can_be_reshuffled_dict.update({y[0]:y[1]})

            boolean_check, allocation_result = \
                imp_funcs.check_if_inquiry_can_be_booked_and_get_allocation_rec(bookings_can_be_reshuffled_dict,
                                                                                allocated_bookings_dict,
                                                                                setCars,
                                                                                hard_coded_allocation_rec)

            if boolean_check == 1:
                if is_converted_dict[y[0]] == 1:
                    setCars, AllocationRecord = imp_funcs.update_car_schedule_and_allocation_record(
                        allocation_result, hard_coded_allocation_rec,
                        setCars, bookings_can_be_reshuffled_dict)
                    allocated_bookings_dict.update({y[0]: y[1]})
            else:
                empty_search_bookings.update({y[0]: y[1]})
                del bookings_can_be_reshuffled_dict[y[0]]
                setCars, AllocationRecord = imp_funcs.update_car_schedule_and_allocation_record(
                    AllocationRecord, hard_coded_allocation_rec,
                    setCars, bookings_can_be_reshuffled_dict)

    for i in allocated_bookings_dict.keys():
        totalRevenue += allocated_bookings_dict[i].bookingLength

    return setCars, AllocationRecord, empty_search_bookings, totalRevenue



