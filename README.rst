About
=====
***This project is looking for a maintainer - Please contact me if you're interested***


Originally taken from the blog post by Roland Tapken at:
http://www.blogs.uni-osnabrueck.de/rotapken/2008/12/03/create-screenshots-of-a-web-page-using-python-and-qtwebkit/

Installation
============

Ubuntu
------
- Add following packages: apt-get install python-qt4 libqt4-webkit xvfb
- Install the flash plugin to screenshot Adobe Flash files: apt-get install flashplugin-installer

Automated installation via pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Install pip: apt-get install python-pip
- Install webkit2png: pip install webkit2png

Manual installation via Git
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Install git: apt-get install git-core
- Create directory: mkdir python-webkit2png
- Clone the project: git clone https://github.com/adamn/python-webkit2png.git python-webkit2png
- Install with: python python-webkit2png/setup.py install

FreeBSD
-------
- install qt4 webkit: www/py-qt4-webkit, www/qt4-webkit, devel/py-qt4
- install pip: devel/py-pip
- install via: pip install webkit2png

Usage
=====
- On a headless server run: python scripts/webkit2png [options] <URL>
- For help run: python scripts/webkit2png -h