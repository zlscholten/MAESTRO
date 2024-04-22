## Description: This file contains the functions for communication between the Raspberry Pi and the Nucleo board. ##

## Import Libraries ##
import spidev
import gpiozero
import matplotlib.pyplot as plotter

## Define Constants ##
SPI_BUS = 0
SPI_DEVICE = 0
SPI_FREQ = 6400000
TRIGGER_PIN = 4
BITS_PER_BYTE = 8
BYTES_PER_SAMPLE = 4
BYTES_DATA_LENGTH = 2
CPI_INDEX = 2

## Function Definitions ##
# Function to create spi object.
def create_spi():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_FREQ
    return spi

# Function to destroy spi object.
def destroy_spi(spi):
    spi.close()

# Function to create trigger object.
def create_trigger():
    trigger = gpiozero.DigitalInputDevice(TRIGGER_PIN)
    return trigger

# Function to destroy trigger object.
def destroy_trigger(trigger):
    trigger.close()

# Function to combine two single byte integers into a single two-byte integer.
def combine(upper, lower):
    return (upper << BITS_PER_BYTE) | lower

# Function to separate a single two-byte integer into two single byte integers.
def separate(data):
    lower = data & 0xFF
    upper = (data >> BITS_PER_BYTE) & 0xFF
    return upper, lower

# Function to extract data_1 and data_2 from data_bytes.
def extract(data_bytes):
    # Create data_1 and data_2
    data_1 = [0 for _ in range(len(data_bytes) // BYTES_PER_SAMPLE)]
    data_2 = [0 for _ in range(len(data_bytes) // BYTES_PER_SAMPLE)]

    # Extract data_1 and data_2 from data_bytes
    for i in range(0, len(data_bytes), BYTES_PER_SAMPLE):
        data_1_lower = data_bytes[i + 2]
        data_1_upper = data_bytes[i + 3]
        data_1[i // BYTES_PER_SAMPLE] = combine(data_1_lower, data_1_upper)

        data_2_lower = data_bytes[i]
        data_2_upper = data_bytes[i + 1]
        data_2[i // BYTES_PER_SAMPLE] = combine(data_2_lower, data_2_upper)

    # Return data_1 and data_2
    return data_1, data_2 

# Function to transmit data_tx to the Nucleo board and receive data_rx_1 and data_rx_2 from the Nucleo board.
def comm(data_tx):
    # Reformat data_tx
    data_tx = [data_tx[0], data_tx[1], data_tx[2], data_tx[3], data_tx[4], data_tx[5], *separate(data_tx[6])]
    
    # Create spi, trigger, data_rx_1, and data_rx_2
    spi = create_spi()
    trigger = create_trigger() 
    data_rx_1 = [None for _ in range(data_tx[CPI_INDEX])]
    data_rx_2 = [None for _ in range(data_tx[CPI_INDEX])]

    # Transmit data_tx, receive data_length, and receive data_rx_1 and data_rx_2
    spi.xfer3(data_tx)
    trigger.wait_for_active()
    data_length_dummy = [0 for _ in range(BYTES_DATA_LENGTH)]
    data_length = BYTES_PER_SAMPLE * combine(*spi.xfer3(data_length_dummy))
    data_rx_dummy = [0 for _ in range(data_length)]
    for i in range(data_tx[CPI_INDEX]):
        trigger.wait_for_active()
        data_rx_1[i], data_rx_2[i] = extract(spi.xfer3(data_rx_dummy))

    # Destroy spi and trigger objects
    destroy_spi(spi)
    destroy_trigger(trigger)
    
    # Return data_rx_1 and data_rx_2
    return data_rx_1, data_rx_2

# Function to test the comm function.
def test_comm():
    # Set data_tx values
    random_phase_chip = 1
    random_on_time = 1
    num_cpi = 1
    num_pulse = 5
    num_chip = 13
    num_cycle = 20
    pri_length = 65000
    
    # Create data_tx
    data_tx = [random_phase_chip, random_on_time, num_cpi, num_pulse, num_chip, num_cycle, pri_length]

    # Transmit data_tx and receive data_rx_1 and data_rx_2
    data_rx_1, data_rx_2 = comm(data_tx)
    
   # Create a time axis
    time_1 = list(range(1, len(data_rx_1) + 1))
    time_2 = list(range(1, len(data_rx_2) + 1))

    # Create a plot
    plotter.plot(time_1, data_rx_1, time_2, data_rx_2)

    # Display the plot
    plotter.show()
    
    # Wait for user input
    input("Press Enter to continue...")

## Main ##
if __name__ == "__main__":
    test_comm()