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
#
# Nice ideas "todo":
#  - Add QTcpSocket support to create a "screenshot daemon" that
#    can handle multiple requests at the same time.

from webkit2png import WebkitRenderer

import sys
import signal
import os
import urlparse
import logging
from optparse import OptionParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *

VERSION="20091224"
LOG_FILENAME = 'webkit2png.log'
logger = logging.getLogger('webkit2png');

def init_qtgui(display=None, style=None, qtargs=None):
    """Initiates the QApplication environment using the given args."""
    if QApplication.instance():
        logger.debug("QApplication has already been instantiated. \
                        Ignoring given arguments and returning existing QApplication.")
        return QApplication.instance()

    qtargs2 = [sys.argv[0]]

    if display:
        qtargs2.append('-display')
        qtargs2.append(display)
        # Also export DISPLAY var as this may be used
        # by flash plugin
        os.environ["DISPLAY"] = display

    if style:
        qtargs2.append('-style')
        qtargs2.append(style)

    qtargs2.extend(qtargs or [])

    return QApplication(qtargs2)


if __name__ == '__main__':
    # This code will be executed if this module is run 'as-is'.

    # Enable HTTP proxy
    if 'http_proxy' in os.environ:
        proxy_url = urlparse.urlparse(os.environ.get('http_proxy'))
        proxy = QNetworkProxy(QNetworkProxy.HttpProxy, proxy_url.hostname, proxy_url.port)
        QNetworkProxy.setApplicationProxy(proxy)

    # Parse command line arguments.
    # Syntax:
    # $0 [--xvfb|--display=DISPLAY] [--debug] [--output=FILENAME] <URL>

    description = "Creates a screenshot of a website using QtWebkit." \
                + "This program comes with ABSOLUTELY NO WARRANTY. " \
                + "This is free software, and you are welcome to redistribute " \
                + "it under the terms of the GNU General Public License v2."

    parser = OptionParser(usage="usage: %prog [options] <URL>",
                          version="%prog " + VERSION + ", Copyright (c) Roland Tapken",
                          description=description, add_help_option=True)
    parser.add_option("-x", "--xvfb", nargs=2, type="int", dest="xvfb",
                      help="Start an 'xvfb' instance with the given desktop size.", metavar="WIDTH HEIGHT")
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
    parser.add_option("-F", "--feature", dest="features", action="append", type="choice",
                      choices=["javascript", "plugins"],
                      help="Enable additional Webkit features ('javascript', 'plugins')", metavar="FEATURE")
    parser.add_option("-w", "--wait", dest="wait", default=0, type="int",
                      help="Time to wait after loading before the screenshot is taken [default: %default]", metavar="SECONDS")
    parser.add_option("-t", "--timeout", dest="timeout", default=0, type="int",
                      help="Time before the request will be canceled [default: %default]", metavar="SECONDS")
    parser.add_option("-W", "--window", dest="window", action="store_true",
                      help="Grab whole window instead of frame (may be required for plugins)", default=False)
    parser.add_option("-T", "--transparent", dest="transparent", action="store_true",
                      help="Render output on a transparent background (Be sure to have a transparent background defined in the html)", default=False)
    parser.add_option("", "--style", dest="style",
                      help="Change the Qt look and feel to STYLE (e.G. 'windows').", metavar="STYLE")
    parser.add_option("", "--encoded-url", dest="encoded_url", action="store_true",
        help="Treat URL as url-encoded", metavar="ENCODED_URL", default=False)
    parser.add_option("-d", "--display", dest="display",
                      help="Connect to X server at DISPLAY.", metavar="DISPLAY")
    parser.add_option("--debug", action="store_true", dest="debug",
                      help="Show debugging information.", default=False)
    parser.add_option("--log", action="store", dest="logfile", default=LOG_FILENAME,
                      help="Select the log output file",)

    # Parse command line arguments and validate them (as far as we can)
    (options,args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    if options.display and options.xvfb:
        parser.error("options -x and -d are mutually exclusive")
    options.url = args[0]

    logging.basicConfig(filename=options.logfile,level=logging.WARN,)

    # Enable output of debugging information
    if options.debug:
        logger.setLevel(logging.DEBUG)

    if options.xvfb:
        # Start 'xvfb' instance by replacing the current process
        server_num = int(os.getpid() + 1e6)
        newArgs = ["xvfb-run", "--auto-servernum", "--server-num", str(server_num), "--server-args=-screen 0, %dx%dx24" % options.xvfb, sys.argv[0]]
        skipArgs = 0
        for i in range(1, len(sys.argv)):
            if skipArgs > 0:
                skipArgs -= 1
            elif sys.argv[i] in ["-x", "--xvfb"]:
                skipArgs = 2 # following: width and height
            else:
                newArgs.append(sys.argv[i])
        logger.debug("Executing %s" % " ".join(newArgs))
        try:
            os.execvp(newArgs[0],newArgs[1:])
        except OSError:
            logger.error("Unable to find '%s'" % newArgs[0])
            print >> sys.stderr, "Error - Unable to find '%s' for -x/--xvfb option" % newArgs[0]
            sys.exit(1)

    # Prepare output ("1" means STDOUT)
    if options.output is None:
        options.output = sys.stdout
    else:
        options.output = open(options.output, "w")

    logger.debug("Version %s, Python %s, Qt %s", VERSION, sys.version, qVersion());

    # Technically, this is a QtGui application, because QWebPage requires it
    # to be. But because we will have no user interaction, and rendering can
    # not start before 'app.exec_()' is called, we have to trigger our "main"
    # by a timer event.
    def __main_qt():
        # Render the page.
        # If this method times out or loading failed, a
        # RuntimeException is thrown
        try:
            # Initialize WebkitRenderer object
            renderer = WebkitRenderer()
            renderer.logger = logger
            renderer.width = options.geometry[0]
            renderer.height = options.geometry[1]
            renderer.timeout = options.timeout
            renderer.wait = options.wait
            renderer.format = options.format
            renderer.grabWholeWindow = options.window
            renderer.renderTransparentBackground = options.transparent
            renderer.encodedUrl = options.encoded_url

            if options.scale:
                renderer.scaleRatio = options.ratio
                renderer.scaleToWidth = options.scale[0]
                renderer.scaleToHeight = options.scale[1]

            if options.features:
                if "javascript" in options.features:
                    renderer.qWebSettings[QWebSettings.JavascriptEnabled] = True
                if "plugins" in options.features:
                    renderer.qWebSettings[QWebSettings.PluginsEnabled] = True

            renderer.render_to_file(url=options.url, file_object=options.output)
            options.output.close()
            QApplication.exit(0)
        except RuntimeError, e:
            logger.error("main: %s" % e)
            print >> sys.stderr, e
            QApplication.exit(1)

    # Initialize Qt-Application, but make this script
    # abortable via CTRL-C
    app = init_qtgui(display = options.display, style=options.style)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QTimer.singleShot(0, __main_qt)
    sys.exit(app.exec_())