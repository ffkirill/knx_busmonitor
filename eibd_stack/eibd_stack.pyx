cimport basic_types
from basic_types cimport String, CArray
from lpdu_types cimport LPDU, L_Data_PDU
from tpdu_types cimport TPDU
from cpython cimport array as c_array

cdef bytes as_bytes(String _str):
    return <bytes> (_str.call())


cdef c_array.array as_array(CArray& seq):
    cdef out_array = c_array.array('i')
    cdef size_t i
    for i in range(seq.call()):
        out_array.append(seq[i])
    return out_array


cdef CArray as_cArray(object seq):
    cdef CArray out_array
    cdef size_t i
    out_array.resize(len(seq))
    for i, val in enumerate(seq):
        out_array[i] = val
    return out_array


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
        ptr = LPDU.fromPacket(as_cArray(packet))
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

    def tpdu_frame(self):
        return TPDUFrame._from_packet_carray((<L_Data_PDU*>self.thisptr).data)

    def data(self):
        return as_array((<L_Data_PDU*>self.thisptr).data)


cdef class TPDUFrame:
    cdef TPDU *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self):
        pass

    def __dealloc__(self):
        del self.thisptr

    @staticmethod
    cdef _from_packet_carray(CArray packet):
        ptr = TPDU.fromPacket(packet)
        tpdu = TPDUFrame()
        tpdu.thisptr = ptr
        return tpdu

    @staticmethod
    def from_packet(packet):
        ptr = TPDU.fromPacket(as_cArray(packet))
        tpdu = TPDUFrame()
        tpdu.thisptr = ptr
        return tpdu

    def decode(self):
        if self.thisptr:
            return as_bytes(self.thisptr.Decode())
