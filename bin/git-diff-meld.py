#!/usr/bin/python

import sys
import os


os.system('meld "%s" "%s"' % (sys.argv[5], sys.argv[2]))
