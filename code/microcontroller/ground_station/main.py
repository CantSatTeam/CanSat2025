from machine import I2C, Pin, UART
import machine
import time

LEDS = False

### --- PINOUT --- ###

LORA_UARTN = 0
LORA_M0P = 15
LORA_M1P = 14
LORA_TXP = 12
LORA_RXP = 13
LORA_AUXP = 10

### --- OPERATING CONSTANTS --- ###

from lora_e32_constants import AirDataRate

LORA_DESIRED_FREQ = 911

DESIRED_ADDH = 0x23
DESIRED_ADDL = 0x61
DESIRED_AIR_DATA_RATE = AirDataRate.AIR_DATA_RATE_000_03	

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
    
def receive_lora(file = None):
    while True:
        if lora.available() > 0:
            code, value = lora.receive_message()
            print(ResponseStatusCode.get_description(code))
            print(value)
            if file != None:
                file.write(value)
                file.flush()
        time.sleep(0.01)
    
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

LORA = True

def init():
    if LORA:
        init_lora()

if __name__ == "__main__":
    try:
        init()
        
    except RuntimeError as e:
        print(f"Error initializing sensors: {e}")
        
    file = open("data.txt", 'a')
    
    # Receive radio readings forever and write them to a file
    while True:
        receive_lora(file)
