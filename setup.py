from distutils.core import setup

from setuptools import find_packages

from upset_plotly import __version__

classifiers = """
Development Status :: 4 - Beta
Environment :: Web Environment
License :: OSI Approved :: Apache Software License
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='upset_plotly',
      version=__version__,
      description='A plotly implementation of UpSet plots using upsetplot',
      author='Finlay Maguire',
      author_email='finlaymaguire@gmail.com',
      url='https://github.com/fmaguire/upset_plotly',
      license='Apache v2.0',
      classifiers=classifiers,
      install_requires=[
          'pandas',
          'numpy',
          'upsetplot',
          'plotly',
          'pytest',
          'kaleido',
      ],
      packages=find_packages(),
      include_package_data=True,
)
