from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy

#ext1 = Extension("pricer", ["hjm/pricer.pyx"])
#ext2 = Extension("copula", ["bcd/copula.pyx"])
#ext3 = Extension("bcdpricer", ["bcd/bcdpricer.pyx"])
#ext4 = Extension("calibration", ["bcd/calibration.pyx"])

setup(
  ext_modules = cythonize("**/*.pyx"),
  include_dirs=[numpy.get_include()],
  #cmdclass = {'build_ext': build_ext}
)