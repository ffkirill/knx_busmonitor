from eibconnection import EIBConnection, EIBBuffer
from eibd_stack import LPDUFrame

def main():
    conn = EIBConnection()
    buf = EIBBuffer()
    sock = conn.EIBSocketURL('ip:52.16.249.130')
    print sock
    conn.EIBOpenBusmonitor()
    while True:
        length = conn.EIBGetBusmonitorPacket(buf)
        print length
        lpdu = LPDUFrame.from_packet(buf.buffer)
        print(lpdu.decode())

if __name__ == '__main__':
    main()

