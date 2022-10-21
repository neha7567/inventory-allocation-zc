from datetime import date, datetime, timedelta
from functools import reduce
import gurobipy as grb
import numpy
import random
from matplotlib import pyplot
import copy
import class_utilities


class Car:
    internalIdRecord = dict()

    def __init__(self, car_id, carGroup, kms_reading):
        self.carID = car_id
        self.carGroup = carGroup
        # self.internalId = Car.getInternalId(carGroup)
        self.schedule = dict()  # empty schedule
        self.age = kms_reading

    """@classmethod
    def getInternalId(cls, carGroup):
        if carGroup in cls.internalIdRecord:
            cls.internalIdRecord[carGroup] += 1
        else:
            cls.internalIdRecord[carGroup] = 1
        return cls.internalIdRecord[carGroup]"""

    def addBooking(self, booking):
        # add booking here, we assume that "canBeBooked" has been checked elsewhere
        if booking.carGroup != self.carGroup:
            print("carGroups differ, not booked")
            return

        dateRange = booking.getDateRange()
        newBookingArr = booking.getDailyBooking()

        for d in dateRange:
            if d not in self.schedule:
                self.schedule[d] = []
            self.schedule[d].append(newBookingArr[d])

        # print("Added booking: ", booking)
        return

    def completeBooking(self, booking):
        self.addBooking(booking)
        self.age += booking.kmsTravelled
        return

    def clearBooking(self, booking):
        dateRange = booking.getDateRange()
        newBookingArr = booking.getDailyBooking()
        self.age -= booking.kmsTravelled

        for d in dateRange:
            self.schedule[d].remove(newBookingArr[d])
        return

    def canBeBooked(self, inquiry):
        # returns True/False
        dateRange = inquiry.getDateRange()
        newBookingArr = inquiry.getDailyBooking()
        for d in dateRange:
            existingScheduleForThisDay = self.schedule.get(d, [])  # array of tuples
            newBookingScheduleForThisDay = newBookingArr[d]  # only 1 tuple
            for microBooking in existingScheduleForThisDay:
                if class_utilities.Utilities.checkIntersection(microBooking, newBookingScheduleForThisDay):
                    return False
        return True

    def getWeight(self, startTime, inquiryTime):
        eligibleDates = [date_car for date_car in self.schedule.keys() if
                         inquiryTime.date() <= date_car <= startTime.date()]
        if eligibleDates:
            eligibleDates = sorted(eligibleDates)
            BookingsByEndTime = sorted(self.schedule[eligibleDates[-1]], key=lambda x: x[1])
            print(BookingsByEndTime)
            maxEndTime = BookingsByEndTime[-1][1]
        else:
            maxEndTime = inquiryTime
        return ((startTime - maxEndTime).total_seconds()) / 3600

        # returns the total weight on a car starting from given time t till end of schedule
        # eligibleDates = [date for date in self.schedule.keys() if date >= startDate] #filter
        # totalMinutes = 0
        # for d in eligibleDates:
        # for startEndTuple in self.schedule[d]:
        # totalMinutes += (startEndTuple[1]-startEndTuple[0]).total_seconds()/60
        # return totalMinutes

    def getUtilization(self, startDate, endDate):
        eligibleDates = [date_car for date_car in self.schedule.keys()
                         if startDate.date() <= date_car <= endDate.date()]  # filter
        timeElapsed = endDate - startDate
        totalMins = timeElapsed.total_seconds() / 60
        utilizedMins = 0
        for d in eligibleDates:
            for startEndTuple in self.schedule[d]:
                utilizedMins += (startEndTuple[1] - startEndTuple[0]).total_seconds() / 60
        return utilizedMins / totalMins

    def get_hours_booked(self):
        hours = 0
        for car_date in self.schedule.keys():
            for tuple_entry in self.schedule[car_date]:
                hours += (tuple_entry[1] - tuple_entry[0]).total_seconds()/3600
        return hours

    def __str__(self):
        # the string representation of objects, can be used in printing
        return "Car: " + self.carGroup + " " + str(self.carID)