import copy
import gurobipy as grb
from datetime import timedelta
import generate_demand_supply as cost_func


def date_range(date1, date2):
    for n in range((date2 - date1).days + 1):
        yield date1 + timedelta(n)


def total_mins_two_dates(startDate, endDate):
    timeElapsed = endDate - startDate
    totalMins = timeElapsed.total_seconds() / 60
    return totalMins


def gen_overlap_sets(allBookings):  # input should be a bookings dictionary
    setBookingOverlap = {}  # dictionary with key i and value is the list of all booking indices which overlap with i
    # including i#.
    # creates the overlap set of booking i#
    # allBookings is the set of all bookings with key as the index and attributes in array

    for i in allBookings.keys():
        setBookingOverlap[i] = []
        for k in allBookings.keys():
            if allBookings[i].overlapBooking(allBookings[k]):
                setBookingOverlap[i].append(k)
        setBookingOverlap[i].remove(i)
    return setBookingOverlap


def get_reshuffleable_bookings_and_hardbooked_allocation_record(allocation_record, booking_dict, current_time,
                                                                critical_hours):
    new_allocation_record = copy.copy(allocation_record)
    reshuffleable_bookings = {}

    for record in allocation_record:
        if booking_dict[record[0]].startTime >= current_time + timedelta(hours=critical_hours):
            reshuffleable_bookings.update(
                {record[0]: booking_dict[record[0]]})  # put this in set of reshufflable bookings dict
            new_allocation_record.remove(record)  # remove from allocation record

    return reshuffleable_bookings, new_allocation_record


def remove_reshuffable_bookings_from_car(car_set, allocation_record, bookings_to_be_reshuffled):
    for record in allocation_record:
        if record[0] in bookings_to_be_reshuffled.keys():
            car_set[record[1]].clearBooking(bookings_to_be_reshuffled[record[0]])
    return car_set


def update_car_schedule_and_allocation_record(allocation_record_from_opt, allocation_record_main,
                                              set_cars, bookings_to_be_allocated):
    for record in allocation_record_from_opt:
        if record[0] in bookings_to_be_allocated.keys():
            allocation_record_main.append((record[0], record[1]))  # update record
            set_cars[record[1]].completeBooking(bookings_to_be_allocated[record[0]])  # update car schedule
    return set_cars, allocation_record_main


def get_critical_bookings(bookings_dict, current_time, critical_hours, is_last):
    critical_dict = {}
    if is_last:
        for b_id in bookings_dict.keys():
            if bookings_dict[b_id].startTime >= current_time:
                critical_dict[b_id] = bookings_dict[b_id]
    else:
        for b_id in bookings_dict.keys():
            if bookings_dict[b_id].startTime < current_time + timedelta(hours=critical_hours):
                critical_dict[b_id] = bookings_dict[b_id]

    return critical_dict


def get_eligible_carids_for_booking(inquiry, setCars):
    eligibleCarsForThisInquiry = []
    for j in setCars:
        if setCars[j].canBeBooked(inquiry):
            eligibleCarsForThisInquiry.append(j)
    return eligibleCarsForThisInquiry


def max_weight_algo_legacy(inquiry, setCars, eligibleCarsForThisInquiry):  # ZC current algorithm, runs in real time.
    # the algo uses FCFS for incoming inquiring and allocates to cars based on max weight rule.
    if eligibleCarsForThisInquiry:
        weightsEligibleCars = {}
        for carKey in eligibleCarsForThisInquiry:
            weightsEligibleCars[carKey] = setCars[carKey].getWeight(inquiry.startTime, inquiry.inquiryTime)
        carKeyWithMaxWeight = min(weightsEligibleCars, key=lambda x: weightsEligibleCars[x])
    else:
        carKeyWithMaxWeight = None
    return carKeyWithMaxWeight


def check_if_inquiry_can_be_booked_and_get_allocation_rec(booking_set_can_be_reshuffled, bookings_taken_so_far_dict,
                                                          car_set, hard_booked_allocation_record):
    booking_set = {**booking_set_can_be_reshuffled, **bookings_taken_so_far_dict}  # all bookings + new inquiry
    setBookingOverlap = gen_overlap_sets(booking_set)  # overlap between all of these
    allocation_model = grb.Model(name="Reshuffling Model")

    total_requests = len(booking_set.keys())  # all bookings + inquiry should get allocated

    allocation_dec = allocation_model.addVars(booking_set, car_set, vtype=grb.GRB.BINARY,
                                              name='allocation_decision')
    allocation_model.addConstrs((sum(allocation_dec[i, j] for j in car_set) <= 1 for i in booking_set),
                                'One booking cannot be on multiple cars')

    allocation_model.addConstrs(
        (allocation_dec[i, j] + allocation_dec[k, j] <= 1 for i in booking_set for j in car_set
         for k in setBookingOverlap[i] if setBookingOverlap[i]),
        'No overlap bookings')

    for record in hard_booked_allocation_record:
        if record[0] in booking_set.keys():
            allocation_model.addConstr(allocation_dec[record[0], record[1]] == 1,
                                       'block allocated inquiries')

    obj = grb.quicksum(allocation_dec[i, j] for i in booking_set for j in car_set) - total_requests

    allocation_model.setObjective(obj, grb.GRB.MAXIMIZE)
    allocation_model.optimize()
    solution = allocation_model.objVal
    allocation_record_result = []

    if solution == 0:
        for i in booking_set:
            for j in car_set:
                if allocation_dec[i, j].X > 0:
                    allocation_record_result.append((i, j))  # This is the new allocation record.

        return True, allocation_record_result
    else:
        return False, []


def hard_allocating_critical_bookings_MIP(critical_bookings, allocated_bookings, setCars,
                                          AllocationRecord, weight_variance):
    # get total number of possible bookings
    # batch_bookings must be a dictionary containing all allocated and unalloacted and the new booking
    batch_bookings = {**critical_bookings, **allocated_bookings}
    setBookingOverlap = gen_overlap_sets(batch_bookings)
    allocation_model = grb.Model(name="MIP Allocation Model")
    num_cars = len(setCars.keys())
    total_hours, total_requests = 0, len(batch_bookings.keys())

    for i in batch_bookings:
        total_hours += batch_bookings[i].bookingLength

    allocation_dec = allocation_model.addVars(batch_bookings, setCars, vtype=grb.GRB.BINARY, name='allocation_decision')

    allocation_model.addConstrs((grb.quicksum(allocation_dec[i, j] for j in setCars) == 1 for i in batch_bookings),
                                'One booking cannot be on multiple cars')
    allocation_model.addConstr((grb.quicksum(allocation_dec[i, j] for j in setCars
                                             for i in batch_bookings) == total_requests),
                               'all requests must be allocated')
    allocation_model.addConstrs(
        (allocation_dec[i, j] + allocation_dec[k, j] <= 1 for i in batch_bookings for j in setCars
         for k in setBookingOverlap[i] if setBookingOverlap[i]),
        'No overlap bookings')

    for record in AllocationRecord:
        if record[0] in batch_bookings.keys():
            allocation_model.addConstr(allocation_dec[record[0], record[1]] == 1,
                                       'block allocated inquiries')

    obj = grb.quicksum(allocation_dec[i, j] * cost_func.depreciation_cost(setCars[j].age,
                                                                          batch_bookings[i].bookingLength)
                       for i in batch_bookings.keys() for j in setCars.keys()) + \
          weight_variance * \
          grb.quicksum((grb.quicksum(allocation_dec[i, j] * batch_bookings[i].bookingLength
                                     for i in batch_bookings)
                        - total_hours / num_cars) ** 2
                       for j in setCars)

    allocation_model.setObjective(obj, grb.GRB.MINIMIZE)
    allocation_model.optimize()
    # solution = allocation_model.objVal

    allocation_record_result = []
    for i in batch_bookings:
        for j in setCars:
            if allocation_dec[i, j].X > 0:
                allocation_record_result.append((i, j))


    # """var_values, allocation_record_result = [], []
    # for v in allocation_model.getVars():
    #     if v.x > 0:
    #         var_values.append((v.varname, v.x))"""

    # print(var_values)
    # allocation_record = compile_res.optimal_var_values_to_alloc_rec(var_values)
    return allocation_record_result

