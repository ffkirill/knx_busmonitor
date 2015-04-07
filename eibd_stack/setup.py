from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(
    name="EIDB Bus Stack",
    version='0.0.1',
    description="""EIBD packet parsing parsing internal wrapped as a python
extension""",
    ext_modules=cythonize(Extension(
        'eibd_stack',
        sources=['eibd_stack.pyx', 'lpdu.cpp', 'tpdu.cpp', 'apdu.cpp',
                 'common.cpp'],
        language='c++',
)))