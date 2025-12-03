from machine import I2C, Pin

i2c = I2C(0, scl=Pin(15), sda=Pin(4))
print(i2c.scan())
