# Created by: Michael Klements
# For Raspberry Pi Desktop Case with OLED Stats Display
# Base on Adafruit Blinka & SSD1306 Libraries
# Installation & Setup Instructions - https://www.the-diy-life.com/add-an-oled-stats-display-to-raspberry-pi-os-bullseye/#!/usr/bin/env python3
# Modified for 128x32 OLED display
import time
import board
import busio
import gpiozero
import subprocess

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Reset pin using gpiozero
oled_reset = gpiozero.OutputDevice(4, active_high=False)

# Display Parameters
WIDTH = 128
HEIGHT = 32
LOOPTIME = 1.0

# I2C Interface
i2c = board.I2C()

# Manual reset pulse
oled_reset.on()
time.sleep(0.1)
oled_reset.off()
time.sleep(0.1)
oled_reset.on()

# OLED display object
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
oled.fill(0)
oled.show()

# Drawing setup
image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Fonts
font = ImageFont.truetype('PixelOperator.ttf', 16)
icon_font = ImageFont.truetype('lineawesome-webfont.ttf', 18)

page = 0  # Toggle display pages

while True:
    # Clear the screen buffer
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    # Collect system info
    IP = subprocess.check_output("hostname -I | cut -d' ' -f1 | head --bytes -1", shell=True).decode().strip()
    CPU = subprocess.check_output("top -bn1 | grep load | awk '{printf \"%.2f%%\", $(NF-2)}'", shell=True).decode().strip()
    MemUsage = subprocess.check_output("free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2 }'", shell=True).decode().strip()
    Disk = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"%d/%dGB\", $3,$2}'", shell=True).decode().strip()
    Temp = subprocess.check_output("vcgencmd measure_temp | cut -d '=' -f 2 | head --bytes -1", shell=True).decode().strip()

    if page == 0:
        # Page 1
        draw.text((0, 5), chr(62609), font=icon_font, fill=255)  # Temp icon
        draw.text((20, 5), Temp, font=font, fill=255)

        draw.text((65, 5), chr(62776), font=icon_font, fill=255)  # Mem icon
        draw.text((85, 5), MemUsage, font=font, fill=255)

    else:
        # Page 2
        draw.text((0, 0), chr(63426), font=icon_font, fill=255)  # Disk icon
        draw.text((20, 0), Disk, font=font, fill=255)

        draw.text((65, 0), chr(62171), font=icon_font, fill=255)  # CPU icon
        draw.text((85, 0), CPU, font=font, fill=255)

        draw.text((0, 18), chr(61931), font=icon_font, fill=255)  # IP icon
        draw.text((20, 18), IP, font=font, fill=255)

    # Display buffer
    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)

    page = 1 - page
