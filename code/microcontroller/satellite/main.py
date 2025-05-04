from machine import I2C, Pin, UART
import machine
import time

LEDS = False

DOUBLE_SCAN = True

FILEPATH = "log.txt"

### --- PINOUT --- ###

I2CN = 1
SDAP = 2
SCLP = 3

NEO_UARTN = 0
NEO_TXP = 16
NEO_RXP = 17

LORA_UARTN = 1
LORA_M0P = 15
LORA_M1P = 14
LORA_TXP = 8
LORA_RXP = 9
LORA_AUXP = 10

LED1P = 18
LED2P = 19
LED3P = 20

### --- OPERATING CONSTANTS --- ###

from lora_e32_constants import AirDataRate

LORA_DESIRED_FREQ = 911

DESIRED_ADDH = 0x23
DESIRED_ADDL = 0x61
DESIRED_AIR_DATA_RATE = AirDataRate.AIR_DATA_RATE_011_48

### --- LEDS --- ###

led1 = None
led2 = None
led3 = None

def init_leds():
    if not LEDS:
        return
    
    global led1, led2, led3
    led1 = machine.Pin(LED1P, machine.Pin.OUT)
    led2 = machine.Pin(LED2P, machine.Pin.OUT)
    led3 = machine.Pin(LED3P, machine.Pin.OUT)

def set_leds(v1, v2, v3):
    if not LEDS:
        return
    
    global led1, led2, led3
    if v1 in [0, 1]:
        led1.value(v1)
    if v2 in [0, 1]:
        led2.value(v2)
    if v3 in [0, 1]:
        led3.value(v3)

### --- MPU --- ###

#from mpu_kalman import MPU6050
#
#mpu = None
#
#def init_mpu():
#    global mpu
#    
#    print("Initializing MPU")
#    
#    mpu = MPU6050(I2CN, SDAP, SCLP) # I2C(0), SDA = GP4, SCL = GP5
#    
#    print("Calibrating gyro...")
#    mpu.callibrate_gyro()
#    print("Calibrating accelerometer...")
#    mpu.callibrate_acc()
#    
#def read_mpu():
#    pitch, roll, dt = mpu.return_angles()
#    return [pitch, roll, dt]
    
### --- BME --- ###
    
from bme680 import BME680_I2C
    
i2c = None
sensor = None
    
def init_bme():
    global i2c, sensor
    
    print("Initializing BME")
    
    # Set up I2C communication
    i2c = I2C(I2CN, sda=Pin(SDAP), scl=Pin(SCLP))

    # Create an instance of the BME680 sensor using the I2C class
    sensor = BME680_I2C(i2c, address=0x77)
    
    time.sleep(1)
    
def read_bme():
    temp = sensor.temperature
    hum = sensor.humidity
    pres = sensor.pressure
    return [temp, hum, pres]
    
### --- NEO --- ###

PRINT_GPS_MESSAGES = False

from micropy_gps import MicropyGPS

gps_serial = None
gps = None

# We do time math here to prevent excessive GPS reading
# GPS is slow but we are fast
first_reading_time_ms = None
first_reading_time_ticks_at = None

def init_neo():
    global gps_serial, gps
    
    print("Initializing NEO")
    
    gps_serial = machine.UART(NEO_UARTN, baudrate=9600, tx=machine.Pin(NEO_TXP), rx=machine.Pin(NEO_RXP))
    gps = MicropyGPS()
    
    # Feed GPS data for a while
    print("Waiting for GPS fix...")
    timeout = time.ticks_ms() + 2000  # 2 seconds
    while time.ticks_ms() < timeout:
        read_neo()
        time.sleep_ms(100)
    
    global first_reading_time_ms, first_reading_time_ticks_at
    
    datetime = get_gps_datetime()
    first_reading_time_ticks_at = time.ticks_ms()
    
    second, minute, hour, day, month, year = datetime
    first_reading_time_s = second + minute * 60 + hour * 3600
    first_reading_time_ms = first_reading_time_s * 1000
    
def get_curr_time_ms():
    return time.ticks_ms() - first_reading_time_ticks_at + first_reading_time_ms
    
def to_dmd(coord): # TODO: wtf is this
    deg, mins, direction = coord
    decimal = deg + mins / 60
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

def get_gps_datetime():
    if gps.timestamp and gps.date:
        hour, minute, second = [int(x) for x in gps.timestamp]
        day, month, year = [int(x) for x in gps.date]
        l = [second, minute, hour, day, month, year]
        
        # if list isn't obviously bad, turn on LED
        if l != [0, 0, 0, 0, 0, 0]:
            set_leds(-1, 1, -1)
            
        return l
    return [0, 0, 0, 0, 0, 0]
        #year += 2000
        #return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            #year, month, day, hour, minute, second)
    #return None
    
def read_neo():
    while gps_serial.any():
        try:
            c = gps_serial.read(1)  # Read 1 byte
            if PRINT_GPS_MESSAGES:
                print(c.decode('utf-8'), end = "")
            gps.update(c.decode('utf-8'))
        except UnicodeError:
            pass  # Skip invalid characters
            # TODO: is this cooked??

    lat = to_dmd(gps.latitude)
    lon = to_dmd(gps.longitude)
    speed = gps.speed[0]
    dir_deg = gps.course

    return [lat, lon, speed, dir_deg]
    
### --- LORA --- ###

from lora_e32 import LoRaE32, print_configuration, Configuration
from lora_e32_operation_constant import ResponseStatusCode, ModeType

uart2 = None
lora = None

def init_lora():
    global uart2, lora
    
    uart2 = UART(LORA_UARTN, baudrate=9600, tx=Pin(LORA_TXP), rx=Pin(LORA_RXP))
    lora = LoRaE32('900T30D', uart2, aux_pin=LORA_AUXP, m0_pin=LORA_M0P, m1_pin=LORA_M1P)
    
    code = lora.begin()
    print("INIT CODE:", ResponseStatusCode.get_description(code))
    
    code = lora.set_mode(ModeType.MODE_0_NORMAL)
    print("MODE CODE:", ResponseStatusCode.get_description(code))
    
    set_lora_frequency(LORA_DESIRED_FREQ)

    time.sleep(1)
    #lora_info()
    
def lora_info():
    code = lora.set_mode(ModeType.MODE_3_PROGRAM)
    print("MODE CODE:", ResponseStatusCode.get_description(code))
    time.sleep(1)
    
    lora.clean_UART_buffer()
    code, data = lora.get_module_information()
    print("INFO CODE:", ResponseStatusCode.get_description(code))
    
    code = lora.set_mode(ModeType.MODE_0_NORMAL)
    print("MODE CODE:", ResponseStatusCode.get_description(code))
    time.sleep(1)
    
def lora_status():
    code, configuration = lora.get_configuration()

    print("STATUS CODE:", code)
    print(configuration)
    print_configuration(configuration)
    
def receive_lora():
    while True:
        if lora.available() > 0:
            code, value = lora.receive_message()
            print(ResponseStatusCode.get_description(code))
            print(value)
    
def send_lora(message):
    global lora
    code = lora.send_transparent_message(message)
    print("SEND STATUS:", ResponseStatusCode.get_description(code))
    
def set_lora_frequency(new_freq=911):
    """
      1. Switches to program mode
      2. Reads the current configuration
      3. Updates frequency, address, and air data rate
      4. Writes the new configuration
      5. Returns to normal mode
    """
    # Switch to program mode
    code = lora.set_mode(ModeType.MODE_3_PROGRAM)
    print("Set Program Mode to Program:", ResponseStatusCode.get_description(code))
    time.sleep(1)
    
    print("Clearing UART Buffer")
    # Clean the UART buffer
    # lora.clean_UART_buffer()
    
    # Retrieve the current configuration
    print("Attempting to get config")
    code, config = lora.get_configuration()
    while code != 1:
        print("Failed to get configuration:", ResponseStatusCode.get_description(code))
        code, config = lora.get_configuration()
    print("Found configuration:")
    print_configuration(config)
        
    # Set frequency, address, and air data rate
    chan_value = new_freq - 862
    config.CHAN = chan_value & 0xFF
    print("\nSetting CHAN to:", hex(config.CHAN))
    
    config.ADDH = DESIRED_ADDH & 0xFF
    print("Setting ADDH to:", hex(config.ADDH))
    
    config.ADDL = DESIRED_ADDL & 0xFF
    print("Setting ADDL to:", hex(config.ADDL))
    
    config.SPED.airDataRate = DESIRED_AIR_DATA_RATE
    print("Setting Air Data Rate to:", hex(config.ADDL))
    
    # Write the new configuration back to the module
    code, config2 = lora.set_configuration(config)
    while code != 1:
        print("Set configuration:", ResponseStatusCode.get_description(code))
        code, config2 = lora.set_configuration(config, permanentConfiguration=True)
    print("\nSuccessfully set config:")
    print_configuration(config2)
    time.sleep(1)
    
    # Return to normal mode
    code = lora.set_mode(ModeType.MODE_0_NORMAL)
    print("Back to Normal Mode:", ResponseStatusCode.get_description(code))
    time.sleep(1)
    
    if code == 1:
        set_leds(1, -1, -1)
    
    return code
    
### --- MAIN --- ###

BME = True
MPU = False
NEO = True
LORA = True

def init():
    if BME:
        init_bme()
    if MPU:
        init_mpu()
    if NEO:
        init_neo()
    if LORA:
        init_lora()
    if LEDS:
        init_leds()
        
def gen_str():
    l = []
    
    if BME:
        temp, hum, pres = read_bme()
        
        # TEMP: 10ths of C, HUMIDITY: 10ths of %, PRESSURE: 10ths of hPa
        temp = int(temp * 10)
        hum = int(hum * 10)
        pres = int(pres * 10)
        
        l += "{},{},{}".format(temp, hum, pres).split(",")
        
    if MPU:
        pass
        #pitch, roll, dt = read_mpu()
        #l += "{:.2f},{:.2f},{:.4f}".format(pitch, roll, dt).split(",")
        
    if NEO:
        lat, lon, speed, dir_deg = read_neo()
        
        # LAT: 10e5ths of deg, LON: 10e5ths of deg, speed = 10ths of knots, DEG = 10ths of degrees
        lat = int(lat * 100000)
        lon = int(lon * 100000)
        speed = int(speed * 10)
        dir_deg = int(dir_deg * 10)
        
        l += "{},{},{},{}".format(lat, lon, speed, dir_deg).split(",")
        
        time_ms = get_curr_time_ms()
        
        # TIMESTAMP: 10 ms's
        l.insert(0, "{}".format(int(time_ms/10)))
        
    if LORA:
        pass
        
    cs_str = ",".join(l) + '\n'
    print("CS STR", cs_str)
    
    with open(FILEPATH, "a") as f:
        f.write(cs_str)
            
    return cs_str

def mini_str():
    print("start mini")
    
    if BME:
        temp, hum, pres = read_bme()
        
        # TEMP: 10ths of C, HUMIDITY: 10ths of %, PRESSURE: 10ths of hPa
        temp = int(temp * 10)
        pres = int(pres * 10)
        
        print("end")
        
        return "{},{}".format(temp, pres)
    print("end")
    return ""

def batch_mini_str():
    l = []
    for i in range(5):
        l.append(mini_str())
    cs_str = ",".join(l) + '\n'
    with open(FILEPATH, "a") as f:
        f.write(cs_str)
    return cs_str

if __name__ == "__main__":
    try:
        init()
        
    except RuntimeError as e:
        print(f"Error initializing sensors: {e}")
    
    # Print the sensor readings in an infinite loop
    while True:
        try:
            if not DOUBLE_SCAN:
                generated_str = gen_str()
                if LORA:
                    send_lora(generated_str)
            else:
                generated_str = gen_str()
                if LORA:
                    send_lora(generated_str)
                time.sleep(0.05)
                generated_str = batch_mini_str()
                print("CSM STR:", generated_str)
                if LORA:
                    send_lora(generated_str)

        except RuntimeError as e:
            print(f"Error reading sensors: {e}")
