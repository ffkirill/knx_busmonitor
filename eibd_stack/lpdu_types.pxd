cdef extern from "common.h":
    cdef cppclass CArray:
        CArray(unsigned char[], unsigned) except +
        CArray() except +
        unsigned char& operator[](size_t) nogil
        void resize (unsigned) nogil

cdef extern from "my_strings.h":
    cdef cppclass String:
        const char* call "operator()" () nogil


cdef extern from "lpdu.h":
    cdef cppclass LPDU:
        LPDU() except +
        String Decode() nogil

        @staticmethod
        LPDU * fromPacket(CArray&) except +
