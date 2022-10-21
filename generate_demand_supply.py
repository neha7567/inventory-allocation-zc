from datetime import timedelta
import class_car
import class_inquiry
import numpy as np
import scipy.stats


def generate_car_ages(n):
    return scipy.stats.uniform.rvs(loc=100, scale=90000, size=n, random_state=12)


# generate cars of a given car group
def generate_cars(num_cars, cargroup):
    km_vector = generate_car_ages(num_cars)
    setCars = {}
    for num in range(num_cars):
        setCars[num] = class_car.Car(num, cargroup, km_vector[num])
    return setCars


def clear_all_bookings(carset):
    for i in carset.keys():
        carset[i].schedule = dict()
    return carset


def gen_inquiries_from_real_data(data):
    allInquiries = dict()
    inquiryId = 0
    data = data.sort_values(by='time_stamp', ascending=True)
    sorted_inquiries = []
    # start_date, end_date = min(data.timestamp).date(), max(data.timestamp).date()
    # diff = end_date - start_date
    for index, row in data.iterrows():
        inquiryTime = row.time_stamp
        startTime = row.starts
        endTime = row.ends
        carGroup = "Fiat"  # can implement choice() for different car Groups
        booking = class_inquiry.Inquiry(inquiryId, inquiryTime, startTime,
                                        endTime, carGroup, booked=False)
        allInquiries[inquiryId] = booking
        sorted_inquiries.append((inquiryId, booking))
        inquiryId += 1
    return allInquiries, sorted_inquiries


def generate_distance_matrix_car_inquiry(allInquiries, n):
    random_states = {i : i for i in allInquiries.keys()}
    dist_mat = np.zeros((len(allInquiries.keys()), n))
    for inquiry_id in allInquiries.keys():
        dist_mat[inquiry_id, :] = scipy.stats.uniform.rvs(loc=3, scale=37, size=n,
                                                              random_state=random_states[inquiry_id])
    return dist_mat


def depreciation_cost(km_age_car, booking_length):
    if km_age_car < 50000:
        return 2 * booking_length
    else:
        return .5 * booking_length ** 2


"""def gen_inquiries(start_date, end_date, num, base_price=10):  # num = average number booking per day
    allBookings = dict()
    inquiryId = 0
    diff = end_date - start_date
    for d in range(0, diff.days):  # each day must have around num bookings on average
        numberOfBookingsThisDay = random.randint(1, 2 * num)  # number of bookings we get for a given day d
        inquiryTimeThisDay = [start_date + timedelta(days=10) * random.random() for _ in range(numberOfBookingsThisDay)]
        start_date += timedelta(days=1)
        for n in range(numberOfBookingsThisDay):
            inquiryId += 1
            startTime = inquiryTimeThisDay[n] + timedelta(hours=random.lognormvariate(numpy.log(24), numpy.log(5)))
            endTime = startTime + timedelta(hours=random.uniform(4, 36))
            time_elapsed = (endTime - startTime).total_seconds() / 3600
            exPrice = time_elapsed * base_price
            carGroup = "Fiat"  # can implement choice() for different car Groups
            booking = class_inquiry.Inquiry(inquiryId, inquiryTimeThisDay[n], startTime,
                                            endTime, carGroup, booked=False)
            allBookings[inquiryId] = booking
    return allBookings"""
