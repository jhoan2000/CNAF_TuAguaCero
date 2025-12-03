# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
# Source: Official MicroPython drivers

import framebuf

class SSD1306:
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            0xae,           # DISPLAYOFF
            0x20, 0x00,     # MEMORYMODE
            0x40,           # SETSTARTLINE
            0xa1,           # SEGREMAP
            0xc8,           # COMSCANDEC
            0xda, 0x12,     # SETCOMPINS
            0x81, 0xcf,     # SETCONTRAST
            0xa4,           # DISPLAYALLON_RESUME
            0xa6,           # NORMALDISPLAY
            0xd5, 0x80,     # SETDISPLAYCLOCKDIV
            0x8d, 0x14 if not self.external_vcc else 0x10,  # CHARGEPUMP
            0xaf            # DISPLAYON
        ):
            self.write_cmd(cmd)

        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(0xae)

    def poweron(self):
        self.write_cmd(0xaf)

    def contrast(self, contrast):
        self.write_cmd(0x81)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(0xa7 if invert else 0xa6)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xb0 | page)
            self.write_cmd(0x00)
            self.write_cmd(0x10)
            self.write_data(self.buffer[page * self.width:(page + 1) * self.width])

    def fill(self, col):
        self.framebuf.fill(col)

    def pixel(self, x, y, col):
        self.framebuf.pixel(x, y, col)

    def scroll(self, dx, dy):
        self.framebuf.scroll(dx, dy)

    def text(self, string, x, y, col=1):
        self.framebuf.text(string, x, y, col)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, bytearray([0x40]) + buf)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.dc.init(self.dc.OUT, value=0)
        self.res.init(self.res.OUT, value=0)
        self.cs.init(self.cs.OUT, value=1)
        self.reset()
        super().__init__(width, height, external_vcc)

    def reset(self):
        self.res(1)
        self.res(0)
        self.res(1)

    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)
