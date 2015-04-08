from eibconnection import EIBConnection, EIBBuffer
from eibd_stack import LPDUFrame, LPDUDataFrame
import time
import select
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


def telegram_ready(buf):
    lpdu = LPDUFrame.from_packet(buf.buffer)
    if isinstance(lpdu, LPDUDataFrame):
        print('''repeated: {}
valid length: {}
valid checksum: {}
source: {}
destination address type: {}
destination: {}
hops: {}
priority: {}
tpdu_frame: {}
layer 4 raw data: {}''').format(
            lpdu.repeated,
            lpdu.valid_length,
            lpdu.valid_checksum,
            lpdu.source,
            addr_types[lpdu.addr_type],
            lpdu.destination,
            lpdu.hops,
            prios[lpdu.priority],
            lpdu.tpdu_frame().decode(),
            lpdu.data()
        )
    else:
        print(lpdu.decode())


def main():
    conn = EIBConnection()
    buf = EIBBuffer()

    # open socket
    if conn.EIBSocketURL('ip:52.16.249.130') == -1:
        raise RuntimeError('Connection open failed')

    fd = conn.EIB_Poll_FD()

    # request open bus monitor
    if conn.EIBOpenBusmonitor_async() == -1:
        raise RuntimeError('Open bus monitor request failed')

    while True:
        select.select([fd], [], [])
        res = conn.EIB_Poll_Complete()
        if res == 1:
            conn.EIBComplete()
            break
        elif res == -1:
            raise RuntimeError('Could not poll open bus monitor')

    # request data
    while True:
        conn.EIBGetBusmonitorPacket_async(buf)
        select.select([fd], [], [])
        res = conn.EIB_Poll_Complete()
        if res == 1:
            conn.EIBComplete()
            telegram_ready(buf)
        elif res == -1:
            raise RuntimeError('Could not poll bus monitor packet')


if __name__ == '__main__':
    main()

