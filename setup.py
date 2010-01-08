import os
from setuptools import setup, find_packages

version = '0.8.1'

description = "Takes snapshot of webpages using Webkit and Qt4"
cur_dir = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(cur_dir, 'README.rst')).read()
except:
    long_description = description

setup(
    name = "webkit2png",
    version = version,
    url = 'http://github.com/AdamN/python-webkit2png',
    license = 'LGPL',
    description = description,
    long_description = long_description,
    author = 'Roland Tapken',
    author_email = 'roland at dau-sicher de',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['pyqt4'],
    entry_points="""
    [console_scripts]
    ghi = github.issues:main
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
        'Topic :: Utilities'
    ],
)

