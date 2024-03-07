import utime

pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
pinC7.value(0)
utime.sleep_ms(20)

pinC7.value(1)
utime.sleep_us(2000)
pinC7.value(0)
utime.sleep_ms(18)

utime.sleep_ms(300)

pinC7.value(1)
pinC7.value(0)

pinC7.value(1)
utime.sleep_us(500)
pinC7.value(0)
utime.sleep_ms(19)

utime.sleep_ms(100)

pinC7.value(1)
pinC7.value(0)










    
