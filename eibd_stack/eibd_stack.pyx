from lpdu_types cimport LPDU, String, CArray

cdef bytes as_bytes(String _str):
    return <bytes> (_str.call())

cdef LPDU* _lpdu_from_packet(object packet):
    cdef CArray packet_carray
    cdef size_t i
    packet_carray.resize(len(packet))
    for i, val in enumerate(packet):
        packet_carray[i] = val
    return LPDU.fromPacket(packet_carray)

cdef class LPDUFrame:
    cdef LPDU *thisptr      # hold a C++ instance which we're wrapping

    def __cinit__(self):
        pass

    def __dealloc__(self):
        del self.thisptr

    @staticmethod
    def from_packet(packet):
        lpdu = LPDUFrame()
        lpdu.thisptr = _lpdu_from_packet(packet)
        return lpdu

    def decode(self):
        if self.thisptr:
            return as_bytes(self.thisptr.Decode())
