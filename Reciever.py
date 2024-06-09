# Open Signal, go to "message to self", and then put your cursor in the message box. 
# When this code runs, it will send you a Signal message with the signal strength and GPS coordinate you transmitted from.

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries, Tony DiCola, Kody Kinzie, Skynet
# SPDX-License-Identifier: MIT

import board
import busio
import digitalio
import neopixel
import adafruit_rfm9x
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1106
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# Initialize HID keyboard
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Delay to avoid race conditions on some systems
time.sleep(1)

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize I2C interface
i2c = busio.I2C(scl=board.SCL, sda=board.SDA)
# Setup the I2C display
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# Define the width and height of the display
WIDTH = 130
HEIGHT = 64
# Initialize the SH1106 display
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT, rotation=180)

# Setup NeoPixel for visual feedback
pixel = neopixel.NeoPixel(board.IO10, 2, brightness=0.2)
pixel[0] = (0, 0, 255)
pixel[1] = (0, 0, 255)

# Define radio frequency
RADIO_FREQ_MHZ = 915.0

# Define pins connected to the LoRa chip
CS = digitalio.DigitalInOut(board.IO9)
RESET = digitalio.DigitalInOut(board.IO4)

# Initialize SPI bus
spi = busio.SPI(board.IO6, MOSI=board.IO8, MISO=board.IO7)

# Initialize the RFM9x LoRa radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Set radio parameters
rfm9x.tx_power = 23  # Set transmit power to maximum (23 dB)
rfm9x.coding_rate = 5  # Set coding rate for forward error correction
rfm9x.signal_bandwidth = 125000  # Set signal bandwidth to 125 kHz
rfm9x.enable_crc = True  # Enable cyclic redundancy check for error detection
rfm9x.auto_agc = True  # Enable automatic gain control
rfm9x.preamble_length = 12  # Set the preamble length
rfm9x.low_data_rate_optimize = True  # Enable low data rate optimization

# Main loop to receive LoRa packets
while True:
    # Try to receive a packet
    packet = rfm9x.receive()
    
    # Check if a packet was received
    if packet is None:
        # No packet received, set NeoPixel to red
        pixel[0] = (255, 0, 0)
        pixel[1] = (255, 0, 0)
    else:
        # Packet received, set NeoPixel to green
        pixel[0] = (0, 255, 0)
        
        # Convert the packet to ASCII text
        packet_text = str(packet, "ascii")
        
        # Get the signal strength of the received packet
        rssi = rfm9x.last_rssi

        # Print the received message and signal strength to the console
        print("Received (ASCII): {0}".format(packet_text))
        print("Received signal strength: {0} dB".format(rssi))

        # Type out the received message and signal strength using HID keyboard
        keyboard_layout.write("Message received: " + packet_text)
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
        time.sleep(.25)

        keyboard_layout.write(f"Signal strength: {rssi} dB")
        keyboard.press(Keycode.ENTER)
        keyboard.release_all()
