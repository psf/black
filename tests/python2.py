#!/usr/bin/env python2

import sys

print >> sys.stderr , "Warning:" ,
print >> sys.stderr , "this is a blast from the past."
print >> sys.stderr , "Look, a repr:", `sys`


def function((_globals, _locals)):
    exec ur"print 'hi from exec!'" in _globals, _locals


function((globals(), locals()))


# output


#!/usr/bin/env python2

import sys

print >>sys.stderr, "Warning:",
print >>sys.stderr, "this is a blast from the past."
print >>sys.stderr, "Look, a repr:", ` sys `


def function((_globals, _locals)):
    exec ur"print 'hi from exec!'" in _globals, _locals


function((globals(), locals()))
