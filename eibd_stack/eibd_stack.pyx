cimport basic_types
from lpdu_types cimport (LPDU, L_Data_PDU, String, CArray)


cdef bytes as_bytes(String _str):
    return <bytes> (_str.call())


cdef LPDU* _lpdu_from_packet(object packet):
    cdef CArray packet_carray
    cdef size_t i
    packet_carray.resize(len(packet))
    for i, val in enumerate(packet):
        packet_carray[i] = val
    return LPDU.fromPacket(packet_carray)


cdef class EIBAddr:
    addr = []
    def __cinit__(self, addr):
        self.addr[:] = [(addr >> 12) & 0xf, (addr >> 8) & 0xf, (addr) & 0xff]

    def __str__(self):
        return '{}.{}.{}'.format(*self.addr)


cdef class GroupAddr:
    addr = []
    def __cinit__(self, addr):
        self.addr[:] = [(addr >> 11) & 0x1f, (addr >> 8) & 0x7, (addr) & 0xff]

    def __str__(self):
        return '{}/{}/{}'.format(*self.addr)


cdef class LPDUFrame:
    cdef LPDU *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self):
        pass

    def __dealloc__(self):
        del self.thisptr

    @staticmethod
    def from_packet(packet):
        ptr = _lpdu_from_packet(packet)
        if <L_Data_PDU*?> ptr:
            lpdu = LPDUDataFrame()
        else:
            lpdu = LPDUFrame()
        lpdu.thisptr = ptr
        return lpdu

    def decode(self):
        if self.thisptr:
            return as_bytes(self.thisptr.Decode())



cdef class LPDUDataFrame(LPDUFrame):
    GROUP_ADDRESS = basic_types.GroupAddress
    INDIVIDUAL_ADDRESS = basic_types.IndividualAddress

    PRIO_LOW = basic_types.PRIO_LOW
    PRIO_NORMAL = basic_types.PRIO_NORMAL
    PRIO_URGENT = basic_types.PRIO_URGENT
    PRIO_SYSTEM = basic_types.PRIO_SYSTEM

    @property
    def repeated(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).repeated

    @property
    def valid_checksum(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).valid_checksum

    @property
    def valid_length(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).valid_length

    @property
    def addr_type(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).AddrType

    @property
    def source(self):
        if self.thisptr:
            return EIBAddr((<L_Data_PDU*>self.thisptr).source)

    @property
    def destination(self):
        if self.thisptr:
            if self.addr_type == self.GROUP_ADDRESS:
                return GroupAddr((<L_Data_PDU*>self.thisptr).dest)
            else:
                return EIBAddr((<L_Data_PDU*>self.thisptr).dest)

    @property
    def hops(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).hopcount

    @property
    def priority(self):
        if self.thisptr:
            return (<L_Data_PDU*>self.thisptr).prio
