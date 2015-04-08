from libcpp cimport bool
from basic_types cimport CArray, String, EIB_AddrType, eibaddr_t, EIB_Priority

cdef extern from "lpdu.h":
    cdef cppclass LPDU:
        LPDU() except +
        String Decode() nogil

        @staticmethod
        LPDU * fromPacket(CArray&) except +

    cdef cppclass L_Data_PDU(LPDU):
        bool repeated
        bool valid_checksum
        bool valid_length
        EIB_AddrType AddrType
        eibaddr_t source
        eibaddr_t dest
        unsigned char hopcount
        EIB_Priority prio
