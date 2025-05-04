class Altitude():
    _SEA_LEVEL_PRESSURE = 1013.25

    _EXP = 0.1903
    _DENOM = 0.0000225577

    # metres
    def altitude(pres):
        return (1 - pow(pres / Altitude._SEA_LEVEL_PRESSURE, Altitude._EXP)) / Altitude._DENOM

class Packet():
    LONG_PACKET_LENGTH = 8
    MINI_PACKET_LENGTH = 3
    
    def __init__(self, packet):
        parts = packet.strip().split(',')

        if len(parts) == 8:
            self.handle_full_packet(parts)

    def handle_full_packet(self, parts):
        # [0] = timestamp (NEO)
        # [1] = temp, [2] = hum, [3] = pres (BME)
        # [4] = lat, [5] = lon, [6] = speed, [7] = dir_deg (NEO)

        if len(parts) != 8:
            raise ValueError("Invalid packet format or sensor not enabled")

        # ms
        self.time = int(parts[0]) * 10
        # degrees C
        self.temp = int(parts[1]) / 10
        # %
        self.hum = int(parts[2]) / 10
        # hPa
        self.pres = int(parts[3]) / 10
        # degrees
        self.lat = int(parts[4]) / 100000
        self.lon = int(parts[5]) / 100000
        # knots
        self.speed = int(parts[6]) / 10
        # degrees
        self.dir_deg = int(parts[7]) / 10

    def print(self):
        print(f"Time: {self.time}ms, Temp: {self.temp}C, Hum: {self.hum}%, Pres: {self.pres}hPa, Lat: {self.lat}, Lon: {self.lon}, Speed: {self.speed}kts, Dir: {self.dir_deg}deg, Alt: {self.altitude()}m")

    def altitude(self):
        return Altitude.altitude(self.pres)
