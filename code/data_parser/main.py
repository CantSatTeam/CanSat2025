from packet import Packet
from amdar import AMDAR
from sim import Sim

if __name__ == "__main__":
    f = open("in.txt", 'r')
    data = f.readlines()
    f.close()

    packets = []
    for line in data:
        l = line.strip().split(',')
        if len(l) == Packet.LONG_PACKET_LENGTH:
            packet = Packet(line)
            packet.print()
            packets.append(packet)

    with open("out.txt", 'w') as o:
        amdar = AMDAR.generate_string(packets)
        o.write(amdar)

    with open("sim.txt", 'w') as s:
        for packet in packets:
            sim = Sim.generate_string(packet)
            s.write(sim)
            print(sim)
