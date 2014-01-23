from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.tinymcetiles',
      version=version,
      description="TinyMCE Plugin for Tiles",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Rob Gietema',
      author_email='rob@fourdigits.nl',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.tiles',
          'plone.app.blocks',
          'Products.TinyMCE',
      ],
      extras_require={
        'test': ['plone.app.testing'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
