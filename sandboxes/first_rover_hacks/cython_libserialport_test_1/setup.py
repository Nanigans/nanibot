from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = Extension(
    "bno055_read_test",
    sources=["bno055_read_test.pyx","sensor_read_test_5.c","serialport.c","linux.c","linux_termios.c"],
    include_dirs = ["/home/pi/libserialport"]
)

setup(
    ext_modules = cythonize(extensions)
)
