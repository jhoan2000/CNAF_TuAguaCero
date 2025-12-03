from machine import Pin, I2C
import framebuf
import time

class SH1107:
    def __init__(self, i2c, width=128, height=64, addr=0x3C, rst=None):
        self.i2c = i2c
        self.addr = addr
        self.width = width
        self.height = height
        self.pages = self.height // 8
        self.buffer = bytearray(self.width * self.pages)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        if rst:
            rst.value(0)
            time.sleep_ms(50)
            rst.value(1)
            time.sleep_ms(50)

        self.init()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x00, cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b"\x40" + buf)

    def init(self):
        cmds = [
            0xAE,       # Display off
            0xD5, 0x50, # Clock divide ratio
            0x20,       # Memory addressing mode (Page)
            0xA0,       # Segment remap
            0xC0,       # Com scan direction
            0xDA, 0x12, # COM pins
            0x81, 0x80, # Contrast
            0xA4,       # Display follows RAM content
            0xA6,       # Normal display
            0xAF        # Display on
        ]
        for c in cmds:
            self.write_cmd(c)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            start = page * self.width
            end = start + self.width
            self.write_data(self.buffer[start:end])
