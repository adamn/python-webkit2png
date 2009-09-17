#!/usr/bin/env python
#
# webkit2png.py
#
# Creates screenshots of webpages using by QtWebkit.
#
# Copyright (c) 2008 Roland Tapken <roland@dau-sicher.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

import sys
import signal
import os
import logging
LOG_FILENAME = 'webkit2png.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.WARN,)
import time

from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage

# Class for Website-Rendering. Uses QWebPage, which
# requires a running QtGui to work.
class WebkitRenderer(QObject):

    # Initializes the QWebPage object and registers some slots
    def __init__(self):
        logging.debug("Initializing class %s", self.__class__.__name__)
        self._page = QWebPage()
        self.connect(self._page, SIGNAL("loadFinished(bool)"), self.__on_load_finished)
        self.connect(self._page, SIGNAL("loadStarted()"), self.__on_load_started)
        self.connect(self._page.networkAccessManager(), SIGNAL("sslErrors(QNetworkReply *,const QList<QSslError>&)"), self.__on_ssl_errors)

        # The way we will use this, it seems to be unesseccary to have Scrollbars enabled
        self._page.mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self._page.mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        # Helper for multithreaded communication through signals 
        self.__loading = False
        self.__loading_result = False

    # Loads "url" and renders it.
    # Returns QImage-object on success.
    def render(self, url, width=0, height=0, timeout=0):
        logging.debug("render(%s, timeout=%d)", url, timeout)

        # This is an event-based application. So we have to wait until
        # "loadFinished(bool)" raised.
        cancelAt = time.time() + timeout
        self._page.mainFrame().load(QUrl(url))
        while self.__loading:
            if timeout > 0 and time.time() >= cancelAt:
                raise RuntimeError("Request timed out")
            QCoreApplication.processEvents()

        logging.debug("Processing result")

        if self.__loading_result == False:
            raise RuntimeError("Failed to load %s" % url)

        # Set initial viewport (the size of the "window")
        size = self._page.mainFrame().contentsSize()
        if width > 0:
            size.setWidth(width)
        if height > 0:
            size.setHeight(height)
        self._page.setViewportSize(size)

        # Paint this frame into an image
        image = QImage(self._page.viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self._page.mainFrame().render(painter)
        painter.end()

        return image


    # Eventhandler for "loadStarted()" signal
    def __on_load_started(self):
        logging.debug("loading started")
        self.__loading = True

    # Eventhandler for "loadFinished(bool)" signal
    def __on_load_finished(self, result):
        logging.debug("loading finished with result %s", result)
        self.__loading = False
        self.__loading_result = result

    # Eventhandler for "sslErrors(QNetworkReply *,const QList<QSslError>&)" signal
    def __on_ssl_errors(self, reply, errors):
        logging.warn("ssl error")
        #self.__loading = False
        #self.__loading_result = result
        reply.ignoreSslErrors()


if __name__ == '__main__':
    # Parse command line arguments.
    # Syntax:
    # $0 [--xvfb|--display=DISPLAY] [--debug] [--output=FILENAME] <URL>
    qtargs = [sys.argv[0]]

    description = "Creates a screenshot of a website using QtWebkit." \
                + "This program comes with ABSOLUTELY NO WARRANTY. " \
                + "This is free software, and you are welcome to redistribute " \
                + "it under the terms of the GNU General Public License v2."

    parser = OptionParser(usage="usage: %prog [options] <URL>",
                          version="%prog 0.1, Copyright (c) 2008 Roland Tapken",
                          description=description)
    parser.add_option("-x", "--xvfb", action="store_true", dest="xvfb",
                      help="Start an 'xvfb' instance.", default=False)
    parser.add_option("-g", "--geometry", dest="geometry", nargs=2, default=(0, 0), type="int",
                      help="Geometry of the virtual browser window (0 means 'autodetect') [default: %default].", metavar="WIDTH HEIGHT")
    parser.add_option("-o", "--output", dest="output",
                      help="Write output to FILE instead of STDOUT.", metavar="FILE")
    parser.add_option("-f", "--format", dest="format", default="png",
                      help="Output image format [default: %default]", metavar="FORMAT")
    parser.add_option("--scale", dest="scale", nargs=2, type="int",
                      help="Scale the image to this size", metavar="WIDTH HEIGHT")
    parser.add_option("--aspect-ratio", dest="ratio", type="choice", choices=["ignore", "keep", "expand", "crop"],
                      help="One of 'ignore', 'keep', 'crop' or 'expand' [default: %default]")
    parser.add_option("-t", "--timeout", dest="timeout", default=0, type="int",
                      help="Time before the request will be canceled [default: %default]", metavar="SECONDS")
    parser.add_option("-d", "--display", dest="display",
                      help="Connect to X server at DISPLAY.", metavar="DISPLAY")
    parser.add_option("--debug", action="store_true", dest="debug",
                      help="Show debugging information.", default=False)
    
    # Parse command line arguments and validate them (as far as we can)
    (options,args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    if options.display and options.xvfb:
        parser.error("options -x and -d are mutually exclusive")
    options.url = args[0]

    # Enable output of debugging information
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)

    # Add display information for qt (you may also use the environment var DISPLAY)
    if options.display:
        qtargs.append("-display")
        qtargs.append(options.display)

    if options.xvfb:
        # Start 'xvfb' instance by replacing the current process
        newArgs = ["xvfb-run", "--server-args=-screen 0, 640x480x24", sys.argv[0]]
        for i in range(1, len(sys.argv)):
            if sys.argv[i] not in ["-x", "--xvfb"]:
                newArgs.append(sys.argv[i])
        logging.debug("Executing %s" % " ".join(newArgs))
        os.execvp(newArgs[0], newArgs)
        raise RuntimeError("Failed to execute '%s'" % newArgs[0])

    # Prepare outout ("1" means STDOUT)
    if options.output == None:
        qfile = QFile()
        qfile.open(1, QIODevice.WriteOnly)
        options.output = qfile

    # Initialize Qt-Application, but make this script
    # abortable via CTRL-C
    app = QApplication(qtargs)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Initialize WebkitRenderer object
    renderer = WebkitRenderer()

    # Technically, this is a QtGui application, because QWebPage requires it
    # to be. But because we will have no user interaction, and rendering can
    # not start before 'app.exec_()' is called, we have to trigger our "main"
    # by a timer event.
    def __on_exec():
        # Render the page.
        # If this method times out or loading failed, a
        # RuntimeException is thrown
        try:
            image = renderer.render(options.url, 
                                    width=options.geometry[0], 
                                    height=options.geometry[1], 
                                    timeout=options.timeout)

            if options.scale:
                # Scale this image
                if options.ratio == 'keep':
                    ratio = Qt.KeepAspectRatio
                elif options.ratio in ['expand', 'crop']:
                    ratio = Qt.KeepAspectRatioByExpanding
                else:
                    ratio = Qt.IgnoreAspectRatio
                image = image.scaled(options.scale[0], options.scale[1], ratio)
                if options.ratio == 'crop':
                    image = image.copy(0, 0, options.scale[0], options.scale[1])

            image.save(options.output, options.format)
            if isinstance(options.output, QFile):
                options.output.close()
            sys.exit(0)
        except RuntimeError, e:
            logging.error(e.message)
            sys.exit(1)

    # Go to main loop (required)
    QTimer().singleShot(0, __on_exec)
    sys.exit(app.exec_())