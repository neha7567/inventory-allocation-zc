from datetime import date, datetime, timedelta
from functools import reduce
import gurobipy as grb
import numpy
import random
from matplotlib import pyplot
import copy
import scipy.stats
import class_utilities


class Inquiry:
    def __init__(self, inquiryId, inquiryTime, startTime, endTime, carGroup, booked=False, basePrice=10):
        self.inquiryTime = inquiryTime
        self.startTime = startTime
        self.endTime = endTime
        self.carGroup = carGroup
        self.booked = booked
        self.basePrice = basePrice
        self.inquiryId = inquiryId
        self.bookingLength = (endTime - startTime).total_seconds() / 3600
        self.kmsTravelled = self.bookingLength * scipy.stats.uniform.rvs(loc=5, scale=120)
        self.leadTime = (startTime - inquiryTime).total_seconds() / 3600

    def getDateRange(self):
        # return array of dates from d1 to d2
        return [self.startTime.date() + timedelta(days=i) for i in
                range((self.endTime.date() - self.startTime.date()).days + 1)]

    def __str__(self):
        return self.carGroup + " " + str(self.startTime.date()) + " " + str(self.endTime.date())

    def getDailyBooking(self):
        # Breaking down a booking into an array of daily bookings, for example, if a booking is of multiple days,
        # we would want start end time for each day the car is requested
        dateRange = self.getDateRange()
        dailyBooking = {}
        for d in dateRange:
            if d > self.startTime.date() and d < self.endTime.date():
                dailyBooking[d] = (class_utilities.Utilities.getStartOfDay(d), class_utilities.Utilities.getEndOfDay(d))
            elif d > self.startTime.date() and d == self.endTime.date():  # d is endDate
                dailyBooking[d] = (class_utilities.Utilities.getStartOfDay(d), self.endTime)
            elif d < self.endTime.date() and d == self.startTime.date():  #
                dailyBooking[d] = (self.startTime, class_utilities.Utilities.getEndOfDay(d))
            else:
                dailyBooking[d] = (self.startTime, self.endTime)
        return dailyBooking

    def overlapBooking(self, inquiry):
        selfDailyBookingSchedule = self.getDailyBooking()
        inquiryDailyBookingSchedule = inquiry.getDailyBooking()
        for d in selfDailyBookingSchedule.keys():
            selfIntervalForThisDay = selfDailyBookingSchedule[d]
            inquiryIntervalForThisDay = inquiryDailyBookingSchedule.get(d, [])
            if class_utilities.Utilities.checkIntersection(selfIntervalForThisDay, inquiryIntervalForThisDay):
                return True
        return False