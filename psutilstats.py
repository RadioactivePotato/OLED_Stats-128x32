#psutil version coded by Jurgen Pfeifer
#Extends compatability, should run on Debian and Ubuntu
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import time
import psutil as PS
import socket
import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Constants
KB = 1024
MB = KB * 1024
GB = MB * 1024
WIDTH = 128
HEIGHT = 32
FONTSIZE = 16
LOOPTIME = 1.0

# Get IPv4 address from first non-loopback interface
def get_ipv4():
    ifaces = PS.net_if_addrs()
    for key in ifaces:
        if key != "lo":
            iface = ifaces[key]
            for addr in iface:
                if addr.family is socket.AddressFamily.AF_INET:
                    return f"IP {addr.address}"
    return "IP ?"

# Initialize I2C OLED
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
oled.fill(0)
oled.show()

# Create image buffer and drawing context
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("PixelOperator.ttf", FONTSIZE)

page = 0  # Flip between 0 (top half) and 1 (bottom half)

while True:
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    IP = get_ipv4()
    CPU = f"CPU {PS.cpu_percent():.1f}%"
    temps = PS.sensors_temperatures()
    TEMP = f"{temps['cpu_thermal'][0].current:.1f}°C"
    mem = PS.virtual_memory()
    MemUsage = f"Mem {round((mem.used+MB-1)/MB):4d}/{round((mem.total+MB-1)/MB):4d}MB"
    root = PS.disk_usage("/")
    Disk = f"Disk {round((root.used+GB-1)/GB):3d}/{round((root.total+GB-1)/GB):3d}GB"

    if page == 0:
        # Page 1
        draw.text((0, 0), IP, font=font, fill=255)
        draw.text((0, FONTSIZE), CPU, font=font, fill=255)
        draw.text((80, FONTSIZE), TEMP, font=font, fill=255)
    else:
        # Page 2
        draw.text((0, 0), MemUsage, font=font, fill=255)
        draw.text((0, FONTSIZE), Disk, font=font, fill=255)

    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)

    page = 1 - page
