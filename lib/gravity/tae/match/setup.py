from distutils.core import setup, Extension


setup(name = "clev",
      version = "1.0",
      ext_modules = [Extension("gravity.tae.match.clev", ["levdiag.c"])])


