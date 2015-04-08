from eibconnection import EIBConnection, EIBBuffer
from eibd_stack import LPDUFrame, LPDUDataFrame

addr_types = {
    LPDUDataFrame.GROUP_ADDRESS: 'group address',
    LPDUDataFrame.INDIVIDUAL_ADDRESS: 'individual address',
}

prios = {
    LPDUDataFrame.PRIO_LOW: 'low',
    LPDUDataFrame.PRIO_NORMAL: 'normal',
    LPDUDataFrame.PRIO_SYSTEM: 'system',
    LPDUDataFrame.PRIO_URGENT: 'urgent',
}

def main():
    conn = EIBConnection()
    buf = EIBBuffer()
    sock = conn.EIBSocketURL('ip:52.16.249.130')
    conn.EIBOpenBusmonitor()
    while True:
        length = conn.EIBGetBusmonitorPacket(buf)
        lpdu = LPDUFrame.from_packet(buf.buffer)
        if isinstance(lpdu, LPDUDataFrame):
            print('''address type: {}
source: {}
destination: {}
hops: {},
priority: {}''').format(
                addr_types[lpdu.addr_type],
                lpdu.source, lpdu.destination,
                lpdu.hops,
                prios[lpdu.priority]
            )
        print(lpdu.decode())

if __name__ == '__main__':
    main()

