# Created by: Michael Klements
# For Raspberry Pi Desktop Case with OLED Stats Display
# Base on Adafruit Blinka & SSD1306 Libraries
# Installation & Setup Instructions - https://www.the-diy-life.com/add-an-oled-stats-display-to-raspberry-pi-os-bullseye/#!/usr/bin/env python3
# Modified for 128x32 OLED display

import time
import board
import busio
import gpiozero
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

# Use gpiozero to control the reset pin
oled_reset_pin = gpiozero.OutputDevice(4, active_high=False)

# Display Parameters
WIDTH = 128
HEIGHT = 32  # Changed from 64
LOOPTIME = 1.0

# I2C communication
i2c = board.I2C()

# Manual reset pulse
oled_reset_pin.on()
time.sleep(0.1)
oled_reset_pin.off()
time.sleep(0.1)
oled_reset_pin.on()

# Create OLED object
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
oled.fill(0)
oled.show()

# Image and drawing setup
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("PixelOperator.ttf", 16)

page = 0  # Alternating display state

while True:
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    # System information
    IP = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode().strip()
    CPU = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'", shell=True).decode().strip()
    Temp = subprocess.check_output("vcgencmd measure_temp | cut -f2 -d '='", shell=True).decode().strip()

    mem_parts = subprocess.check_output(
        "free -m | awk 'NR==2{printf \"%.1f %.1f %.1f\", $3/1024,$2/1024,($3/$2)*100}'",
        shell=True
    ).decode().strip().split()
    mem_used_gb, mem_total_gb, mem_percent = mem_parts
    mem_display = f"Mem: {mem_used_gb}/{mem_total_gb}GB {mem_percent}%"

    Disk = subprocess.check_output(
        "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'",
        shell=True
    ).decode().strip()

    if page == 0:
        # Page 1
        draw.text((0, 0), f"IP: {IP}", font=font, fill=255)
        draw.text((0, 16), f"{CPU}LA", font=font, fill=255)
        draw.text((80, 16), Temp, font=font, fill=255)
    else:
        # Page 2
        draw.text((0, 0), mem_display, font=font, fill=255)
        draw.text((0, 16), Disk, font=font, fill=255)

    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)

    page = 1 - page

    oled.show()

    # Wait for the next loop
    time.sleep(LOOPTIME)
