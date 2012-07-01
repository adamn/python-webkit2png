About
=====
***This project is looking for a maintainer - Please contact me if you're interested***


Originally taken from the blog post by Roland Tapken at:
http://www.blogs.uni-osnabrueck.de/rotapken/2008/12/03/create-screenshots-of-a-web-page-using-python-and-qtwebkit/

Installation
============

Ubuntu
------
- On ubuntu you need to add following packages: apt-get install python-qt4 libqt4-webkit 
- And then install it with: pip install webkit2png

FreeBSD
-------
- install qt4 webkit: www/py-qt4-webkit, www/qt4-webkit, devel/py-qt4
- install pip: devel/py-pip
- install via: pip install webkit2png

Usage
=====
- on a headless server run: xvfb-run --server-args="-screen 0, 640x480x24" python webkit2png-simple.py
