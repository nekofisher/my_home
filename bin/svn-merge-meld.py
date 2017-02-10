#!/usr/bin/env python

import os
import sys
import subprocess
import shutil

try:
        # path to meld
        meld = "/usr/bin/python /usr/bin/meld"

        base       = sys.argv[1] # The parent of the locally modified file
        current    = sys.argv[2] # The the current version in the repository
        local_copy = sys.argv[3] # A copy of the locally modified file
        merged     = sys.argv[4] # A temporary file containing the final merged version
        local      = sys.argv[5] # The local file that is in conflict

        # Launching meld, the local file is on the left, the current svn file is on
        # the right. Merge changes from the right to the left.
        print cmd
        cmd = [meld, mine, current]

        # check_call traps errors
        subprocess.check_call(cmd)

        # Subversion is expecting the final result of the merged to be contained in
        # the "merged"  temporary file, so we'll copy our result over that
        # temporary.
        subprocess.check_call(["cp", mine, merged])

except:
        print "Error using %s" % os.path.abspath(__file__)
        sys.exit(-1)

