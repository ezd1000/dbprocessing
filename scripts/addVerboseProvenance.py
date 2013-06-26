#!/usr/bin/env python2.6

import itertools
import glob
import os
from optparse import OptionParser
import re
import sys
import traceback
import warnings

from spacepy import pycdf

from rbsp import Version


from dbprocessing import inspector


import dbprocessing.DBlogging as DBlogging
import dbprocessing.dbprocessing as dbprocessing
from dbprocessing import DBUtils

"""
go into the database and get the verbose provencoe for a file
then add that to the global attrs for the file
either putout to the same file or a different file
"""


def getVP(options, dbu, filename):
    """
    go into the db and get the VP
    """
    try:
        vp = dbu.getEntry('File', dbu.getFileID(filename)).verbose_provenance
    except DBUtils.DBNoData:
        return ''
    return vp



if __name__ == '__main__':
    usage = "usage: %prog infile [outfile]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--inplace",
                  dest="inplace", action="store_true",
                  help="Add the verbose provence inplace not to an output file", default=False)
    parser.add_option("-f", "--force",
                  dest="force", action='store_true',
                  help="Allow verbose provence to be overwritten", default=False)
    parser.add_option("-m", "--mission", dest="mission",
                      help="selected mission database", default=None)


    (options, args) = parser.parse_args()

    if len(args) not in [1,2]:
        parser.error("incorrect number of arguments")

    if len(args) == 2 and options.inplace:
        parser.error("Incompatable arguments, outfile and --inplace are mutually exclusive")

    if len(args) == 1 and not options.inplace:
        parser.error("Incomplete arguments, either outfile or --inplace required")

    infile = args[0]
    if not os.path.isfile(infile):
        parser.error("Input file {0} did not exist".format(infile))

    if not os.path.isfile(options.mission):
        parser.error("Mission database {0} did not exist".format(options.mission))

    dbu = DBUtils.DBUtils(options.mission)

    vp = getVP(options, dbu, infile)
    dbu._closeDB()
    
    if not vp: # is ''
        sys.exit(0) # we are done
    
    if len(args) == 2 and not options.inplace: # we had an outfile
        cdf = pycdf.CDF(args[1], infile)
        if 'VERBOSE_PROVENANCE' in cdf.attrs: # does it have the attr?
            if cdf.attrs['VERBOSE_PROVENANCE'] and options.force: # if it is populated only continue if --force
                cdf.attrs['VERBOSE_PROVENANCE'] = vp
        else:
            cdf.attrs['VERBOSE_PROVENANCE'] = vp
        cdf.close()
        
    elif options.inplace: # we did not have an outfile
        cdf = pycdf.CDF(infile)
        cdf.readonly(False)
        if 'VERBOSE_PROVENANCE' in cdf.attrs: # does it have the attr?
            if cdf.attrs['VERBOSE_PROVENANCE'] and options.force: # if it is populated only continue if --force
                cdf.attrs['VERBOSE_PROVENANCE'] = vp
        else:
            cdf.attrs['VERBOSE_PROVENANCE'] = vp
        cdf.close()

        
