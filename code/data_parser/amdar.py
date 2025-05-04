from datetime import datetime
from packet import Packet

class AMDAR:
    def _ms_from_midnight_to_month_seconds(ms_since_midnight, day_of_month):
        seconds_since_midnight = ms_since_midnight / 1000
        seconds_in_previous_days = (day_of_month - 1) * 86400
        total_seconds = seconds_in_previous_days + seconds_since_midnight
        return total_seconds

    @staticmethod
    def generate_string(data: list[Packet]):
        MESSAGE_VERSION = "A01"
        PARAMETER_INDICATION = "#"  # this should represent empty data
        AIRCRAFT_IDENTIFIER = "CA9999"
        COMPRESSION_FLAG = "N"
        TIME_OR_PRESSURE = "1" # not sure about this one
        DEPARTURE_AIRPORT = "CYQL"
        ARRIVAL_AIRPORT = "CYQL"

        HEADER = f"{MESSAGE_VERSION}\n" + \
                 f"{PARAMETER_INDICATION}\n" + \
                 f"{AIRCRAFT_IDENTIFIER},{COMPRESSION_FLAG},{TIME_OR_PRESSURE},{DEPARTURE_AIRPORT},{ARRIVAL_AIRPORT}"

        DATA_BLOCK = HEADER + '\n'

        for packet in data:
            OBSERVATION = "0"

            # Latitude and longitude are in seconds, SNNNNNN
            lat = packet.lat
            lon = packet.lon
            LATITUDE = str(int(lat * 3600))
            LONGITUDE = str(int(lon * 3600))

            # Time is recorded as seconds into the month, 7 
            TIME = str(int(AMDAR._ms_from_midnight_to_month_seconds(packet.time, 27)))

            # Altitude is in tens of feet, NNNN
            ALTITUDE = str(int(packet.altitude() * 3.28084 / 10))

            # Temperature is in tenths of degrees Celsius, SNNN
            TEMPERATURE = str(int(packet.temp * 10))

            # Wind direction is in degrees, NNN
            WIND_DIRECTION = int(packet.dir_deg)

            # Wind speed is in knots, NNN
            WIND_SPEED = int(packet.speed)

            # Roll angle flag is unreported, single letter
            ROLL_ANGLE_FLAG = "U"

            DATA_LINE = f"{OBSERVATION},{LATITUDE},{LONGITUDE},{TIME},{ALTITUDE},{TEMPERATURE},{WIND_DIRECTION},{WIND_SPEED},{ROLL_ANGLE_FLAG}"

            DATA_BLOCK += f"{DATA_LINE}\n"

        return DATA_BLOCK
