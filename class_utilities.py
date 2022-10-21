from datetime import date, datetime, timedelta
from functools import reduce
import gurobipy as grb
import numpy
import random
from matplotlib import pyplot
import copy


class Utilities:
    # just a collection of useful functions, will not make instances of these
    @staticmethod
    def getStartOfDay(dt):
        return datetime(dt.year, dt.month, dt.day)

    @staticmethod
    def getEndOfDay(dt):
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59)

    @staticmethod
    def checkIntersection(interval1, interval2):
        if interval1 == [] or interval2 == []:
            return False
        return not (interval1[1] < interval2[0] or interval1[0] > interval2[1])

    @staticmethod
    def print_bookings(dict_of_inquiries):
        for key in dict_of_inquiries:
            print(key, ': ', dict_of_inquiries[key].__str__())

    @staticmethod
    def print_cars(dict_of_cars):
        for key in dict_of_cars:
            print(key, ': ', dict_of_cars[key].__str__())

    @staticmethod
    def getStartEndWindowForSetOfBookings(allBookings):
        sortedInquiries = sorted(allBookings, key=lambda x: allBookings[x].inquiryTime)
        sortedInquiries = [(s, allBookings[s]) for s in sortedInquiries]
        startDate = sortedInquiries[0][1].inquiryTime.date()
        sortedInquiriesByEndTime = sorted(allBookings, key=lambda x: allBookings[x].endTime)
        sortedInquiriesByEndTime = [(s, allBookings[s]) for s in sortedInquiriesByEndTime]
        endDate = sortedInquiriesByEndTime[-1][1].endTime.date()
        return startDate, endDate