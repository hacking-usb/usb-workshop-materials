#!/usr/bin/env python
import sys
import usb
import array

# This file is meant to be a canvas for you to try control requests your new sample device.
# You can try a variety of requests my modifying this file -- particularly by modifying the 
#
# You probably want to try some 'standard'- and 'vendor'- type requests.
#
# High level references:
#  - http://www.beyondlogic.org/usbnutshell/usb6.shtml


# Constants for the vendor ID and product ID of the device we want to target.
VENDOR_ID  = 0x1D50
PRODUCT_ID = 0x60e7

# Set up some constants that can be OR'd together to build the "REQUEST_TYPE" field of the
# control request's SETUP packet.

# directions
HOST_TO_DEVICE      = (0 << 7)
DEVICE_TO_HOST      = (1 << 7)

# request types
STANDARD_REQUEST    = (0 << 5)
CLASS_REQUEST       = (1 << 5)
VENDOR_REQUEST      = (2 << 5)
RESERVED_REQUEST    = (3 << 5)

# destinations
RECIPIENT_DEVICE    = (0 << 0)
RECIPIENT_INTERFACE = (1 << 0)
RECIPIENT_ENDPOINT  = (2 << 0)
RECIPIENT_OTHER     = (3 << 0)


def control_transfer(device, direction, type, destination, request, index, value, length_or_data):
    """
    Simple wrapper function that asks pyUSB to issue a control transfer for us;
    meant to be easy to use in a script that prints the results of the transfer.

    Args:
        device -- The pyusb device to work with.
        direction -- Sets the direction of the transaction-- either DEVICE_TO_HOST or HOST_TO_DEVICE.
        type -- Sets the type of request; usually one of the _REQUEST constants above.
        destination -- Sets the 'destination' of the request; this would probably better be 
                thought of as the 'context' of the request. Almost always RECIPIENT_DEVICE.

        request - The request number. Valid values include the specification-provided request numbers for standard
                requests, or any number < 256 for a vendor request 
        index -- index argument; < 65536
        value -- value argument; < 65536

        data_or_length -- If this is a HOST_TO_DEVICE request, this should be a byte-string or array.array
            of data to be sent; or an empty array to not send any data. If this is a DEVICE_TO_HOST request,
            this should be the maximum number of bytes we want in response. Must be < 65536.
    """

    try:
        result = dev.ctrl_transfer(direction | type | destination, request, index, value, length_or_data)

        # If we got a raw result, return it.
        if not isinstance(result, array.array):
            return result
       
        # Convert the result into a nice, printable format for the exercise.
        # We'll use whichever method is provided by the python install (py2 vs py3 difference)
        if hasattr(result, 'tobytes'):
            return result.tobytes()
        else:
            return repr(result.tostring())

    except usb.core.USBError as e:
        if e.errno == 32:
            return "STALLED"
        else:
            raise e



#
# The main script starts here.
#

# First, we'll connect to the device itself, if we can. We ask pyusb to find
# the first device with our expected vendor/product ID>
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

# If we didn't find a device, error out!
if dev is None:
    print("Couldn't find a device to play with!")
    sys.exit(0)



# Here's an example that'll read the device's Device Descriptor:

result = control_transfer(
    dev,               # work with the device we just opened
    DEVICE_TO_HOST,    # asking for data _from_ the device
    STANDARD_REQUEST,  # we're making a request that's standardized in the USB spec
    RECIPIENT_DEVICE,  # we're talking about the device itself
    0x06,              # issue a GET_DESCRIPTOR request
    (1 << 8),          # ask for the DEVICE descriptor-- the MSB contains the type of descriptor we want.
    0,                 # language ID = english (almost always ignored),
    32                 # return up to 32 bytes
)

print("device descriptor: {}".format(result))

#
# We don't necessarily know exactly what features this device surfaces.
# Let's try asking it for a particular vendor request.
#

result = control_transfer(
    dev,               # work with the device we just opened
    DEVICE_TO_HOST,    # asking for data _from_ the device
    VENDOR_REQUEST,    # we're checking to see if this device supports our vendor-specific request
    RECIPIENT_DEVICE,  # we're talking about the device itself
    0x0,               # issue vendor request 0
    0,                 # we don't know the arguments to this request; so we'll have to experiment
    0,
    32                 # return up to 32 bytes
)

print("trying vendor request 0: {}".format(result))

#
# Hmmm. It doesn't look like _that_ particular vendor request worked-- but
# this is definitely a good framework for exploring the device! You can try some requests manually,
# but eventually, you really want to get to the point where you're automating things.
#

