from eibconnection import EIBConnection, EIBBuffer
PACKET_READ = 0x00
PACKET_RESPONSE = 0x40
PACKET_WRITE = 0x80


def main():
    conn = EIBConnection()
    buf = EIBBuffer()
    sock = conn.EIBSocketURL('ip:52.16.249.130')
    print sock
    conn.EIBOpenBusmonitorText()
    while True:
        length = conn.EIBGetBusmonitorPacket(buf)
        print length
        print(''.join(chr(i) for i in buf.buffer))

if __name__ == '__main__':
    main()

