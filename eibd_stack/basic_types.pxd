from libc.stdint cimport uint16_t

cdef extern from "common.h":
    cdef cppclass CArray:
        CArray(unsigned char[], unsigned) except +
        CArray() except +
        unsigned char& operator[](size_t) nogil
        void resize (unsigned) nogil
        size_t call "operator()" () nogil

    cdef enum EIB_AddrType:
        GroupAddress
        IndividualAddress

    cdef enum EIB_Priority:
        PRIO_LOW
        PRIO_NORMAL
        PRIO_URGENT
        PRIO_SYSTEM

    ctypedef uint16_t eibaddr_t

cdef extern from "my_strings.h":
    cdef cppclass String:
        const char* call "operator()" () nogil