import utime

pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP)

pinC6.value(0)

sp_pull = 15
sp_return = 1

pinC6.value(1)
utime.sleep_us(2000)
pinC6.value(0)
utime.sleep_ms(19)

utime.sleep_ms(225)

pinC6.value(1)
pinC6.value(0)

pinC6.value(1)
utime.sleep_us(500)
pinC6.value(0)
utime.sleep_ms(19)

utime.sleep_ms(225)

pinC6.value(1)
pinC6.value(0)


    
