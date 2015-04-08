from basic_types cimport CArray, String

cdef extern from "tpdu.h":
    cdef cppclass TPDU:
        TPDU() except +
        String Decode() nogil

        @staticmethod
        TPDU * fromPacket(CArray&) except +