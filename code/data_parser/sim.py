from packet import Packet
import math

class Sim():
    def _compute_wind_shear(p1, p2):
        dir1_rad = math.radians(p1.dir_deg)
        dir2_rad = math.radians(p2.dir_deg)

        u1 = p1 * math.cos(dir1_rad)
        v1 = p1 * math.sin(dir1_rad)
        u2 = p2 * math.cos(dir2_rad)
        v2 = p2 * math.sin(dir2_rad)

        delta_v = math.sqrt((u2 - u1)**2 + (v2 - v1)**2)

        delta_z = p2.altitude() - p1.altitude()

        if delta_z == 0:
            return 0

        shear = delta_v / delta_z
        return shear

    def generate_string(packet: Packet):
        return f"{packet.lat},{packet.lon},{packet.altitude()},{packet.speed},{packet.dir_deg}\n"
