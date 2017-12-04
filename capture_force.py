#!/usr/bin/env python

__author__ = 'Kanishka Ganguly'
__version__ = '1.0.0'
__date__ = 'May 25 2017'

from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit
import time


class force_glove:
    def __init__(self, log_file):
        self.interfaceKit = InterfaceKit()
        self.log_file = log_file
        try:
            self.interfaceKit.setOnAttachHandler(self.interfaceKitAttached)
            self.interfaceKit.setOnDetachHandler(self.interfaceKitDetached)
            self.interfaceKit.setOnErrorhandler(self.interfaceKitError)
            self.interfaceKit.setOnSensorChangeHandler(self.interfaceKitSensorChanged)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

        print("Turning on glove....")

        try:
            self.interfaceKit.openPhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

        print("Waiting for glove to attach....")

        try:
            self.interfaceKit.waitForAttach(10000)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            try:
                self.interfaceKit.closePhidget()
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
                print("Exiting....")
                exit(1)
            print("Exiting....")
            exit(1)
        else:
            print "Glove connected..."
            # self.displayDeviceInfo()
        return

    def setSensorRates(self):
        for i in range(self.interfaceKit.getSensorCount()):
            try:
                self.interfaceKit.setDataRate(i, 2)
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
        return

    def closeForceGlove(self):
        try:
            self.interfaceKit.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
        print("Closed force glove...")
        return

    # Information Display Function
    #def displayDeviceInfo(self):
    #    print("Glove " + self.interfaceKit.getDeviceName() + " found")
    #    print("Number of Sensor Inputs: %i" % (self.interfaceKit.getSensorCount()))

    # Event Handler Callback Functions
    def interfaceKitAttached(self, e):
        attached = e.device
        print("InterfaceKit %i Attached!" % (attached.getSerialNum()))

    def interfaceKitDetached(self, e):
        detached = e.device
        print("InterfaceKit %i Detached!" % (detached.getSerialNum()))

    def interfaceKitError(self, e):
        try:
            source = e.device
            print("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    def interfaceKitSensorChanged(self, e):
        force_data = "%i,%i" % (e.index, e.value)
        self.write_log(force_data)
        print("Sensor %i: %i" % (e.index, e.value))

    def write_log(self, glove_data):
        if glove_data is not None:
            to_log = ('%f,%s\r\n') % (time.time(), glove_data)
            if not self.log_file.closed:
                self.log_file.write(to_log)
