import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
import mlx_cam

if __name__ == "__main__":
    while True:
        import gc

        # The following import is only used to check if we have an STM32 board such
        # as a Pyboard or Nucleo; if not, use a different library
        try:
            from pyb import info

        # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
        except ImportError:
            # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
            i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

        # OK, we do have an STM32, so just use the default pin assignments for I2C1
        else:
            i2c_bus = I2C(1)

        #print("MXL90640 Easy(ish) Driver Test")

        # Select MLX90640 camera I2C address, normally 0x33, and check the bus
        i2c_address = 0x33
        scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
        #print(f"I2C Scan: {scanhex}")

        # Create the camera object and set it up in default mode
        camera = mlx_cam.MLX_Cam(i2c_bus)
        #print(f"Current refresh rate: {camera._camera.refresh_rate}")
        camera._camera.refresh_rate = 10.0
        #print(f"Refresh rate is now:  {camera._camera.refresh_rate}")

        # Keep trying to get an image; this could be done in a task, with
        # the task yielding repeatedly until an image is available
        image = None
        while not image:
            image = camera.get_image_nonblocking()
            time.sleep_ms(50)

        #print(f" {time.ticks_diff(time.ticks_ms(), begintime)} ms")

        # Can show image.v_ir, image.alpha, or image.buf; image.v_ir best?
        # Display pixellated grayscale or numbers in CSV format; the CSV
        # could also be written to a file. Spreadsheets, Matlab(tm), or
        # CPython can read CSV and make a decent false-color heat plot.
        
        val = camera.get_csv(image, limits=(0, 99))
        print(val)
        gc.collect()
        #print(f"Memory: {gc.mem_free()} B free")
        time.sleep_ms(100)
