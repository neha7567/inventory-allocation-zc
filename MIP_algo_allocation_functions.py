import scipy.stats
import input_paramteres
import important_function_for_both_algos as imp_func

weight_var = input_paramteres.weight_MIP
critical_hours = input_paramteres.critical_hours


def MIP_with_wait(sortedInquiries, setCars, is_converted_dict):

    booked_hours, empty_search_dict = 0, {}  # total booked hours, empty searches dict
    AllocationRecord = []
    non_allocated_bookings = {}  # bookings accepted but not allocated
    allocated_bookings_dict = {}  # accepted and allocated - hard allocation

    for y in sortedInquiries:
        accepted_bookings = {**allocated_bookings_dict, **non_allocated_bookings}

        is_converted = is_converted_dict[y[0]]
        non_allocated_bookings[y[0]] = y[1]
        can_be_booked, unnecessary_allocation_res = \
            imp_func.check_if_inquiry_can_be_booked_and_get_allocation_rec(non_allocated_bookings,
                                                                           allocated_bookings_dict, setCars,
                                                                           AllocationRecord)
        if can_be_booked == 0:
            del non_allocated_bookings[y[0]]
            empty_search_dict.update({y[0]: y[1]})
        else:
            if is_converted == 0:
                del non_allocated_bookings[y[0]]

        # check if a booking is critical and needs to be allocated
        # when allocating, update the allocated_bookings_dict
        # create a set of critical bookings
        if sortedInquiries.index(y) == len(sortedInquiries) - 1:
            is_last = True
        else:
            is_last = False

        critical_set = imp_func.get_critical_bookings(non_allocated_bookings, y[1].inquiryTime, critical_hours, is_last)
        # allocate these bookings
        allocation_result = imp_func.hard_allocating_critical_bookings_MIP(critical_set, accepted_bookings,
                                                                           setCars, AllocationRecord,
                                                                           weight_var)

        setCars, AllocationRecord = imp_func.update_car_schedule_and_allocation_record(allocation_result,
                                                                                       AllocationRecord,
                                                                                       setCars,
                                                                                       critical_set)
        for b_id in critical_set:
            # batched_for_future_allocations.remove(b_id)
            allocated_bookings_dict.update({b_id: non_allocated_bookings[b_id]})
            del non_allocated_bookings[b_id]  # update unallocated set

        # check if current booking this can be booked ########################
        # add to the dictionary batch_bookings ##############

    for i in allocated_bookings_dict.keys():
        booked_hours += allocated_bookings_dict[i].bookingLength

    return setCars, AllocationRecord, empty_search_dict, booked_hours


def MIP_no_wait(sortedInquiries, setCars, is_converted_dict):
    booked_hours, empty_search_dict = 0, {}
    AllocationRecord = []
    allocated_bookings = {}

    for y in sortedInquiries:
        is_converted = is_converted_dict[y[0]]

        bookings_can_be_reshuffled_dict, hard_coded_allocation_rec = \
            imp_func.get_reshuffleable_bookings_and_hardbooked_allocation_record(AllocationRecord,
                                                                                 allocated_bookings,
                                                                                 y[1].inquiryTime, critical_hours)
        setCars = imp_func.remove_reshuffable_bookings_from_car(setCars, AllocationRecord,
                                                                bookings_can_be_reshuffled_dict)
        bookings_can_be_reshuffled_dict.update({y[0]: y[1]})

        boolean_check, unnecessary_allocation_res = \
            imp_func.check_if_inquiry_can_be_booked_and_get_allocation_rec(bookings_can_be_reshuffled_dict,
                                                                           allocated_bookings,
                                                                           setCars,
                                                                           hard_coded_allocation_rec)
        if boolean_check == 1:
            if is_converted == 1:
                allocation_res = imp_func.hard_allocating_critical_bookings_MIP(bookings_can_be_reshuffled_dict,
                                                                                allocated_bookings,
                                                                                setCars,
                                                                                hard_coded_allocation_rec,
                                                                                weight_var)
                setCars, AllocationRecord = imp_func.update_car_schedule_and_allocation_record(
                                                            allocation_res, hard_coded_allocation_rec,
                                                            setCars, bookings_can_be_reshuffled_dict)
                allocated_bookings.update({y[0]: y[1]})
        else:
            empty_search_dict.update({y[0]: y[1]})
            del bookings_can_be_reshuffled_dict[y[0]]
            setCars, AllocationRecord = imp_func.update_car_schedule_and_allocation_record(
                                                AllocationRecord, hard_coded_allocation_rec,
                                                setCars, bookings_can_be_reshuffled_dict)

    for i in allocated_bookings.keys():
        booked_hours += allocated_bookings[i].bookingLength

        # check if current booking this can be booked ########################
        # add to the dictionary batch_bookings ##############

    return setCars, AllocationRecord, empty_search_dict, booked_hours
