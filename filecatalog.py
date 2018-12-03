#!/usr/bin/python


#https://docs.python.org/2/library/os.html
import os

#https://docs.python.org/2/library/hashlib.html#module-hashlib
import hashlib

#https://docs.python.org/2/tutorial/errors.html
import sys

#https://docs.python.org/3/library/argparse.html
import argparse

#https://docs.python.org/2/library/stat.html
from stat import *


def walkFiles(DEBUG,startdir,suffix):

    #Pull out all the directories and files in the current directory
    for root, dirs, files in os.walk(startdir):
        if DEBUG:
            print("Path: " + str(root))
            for i in dirs:
                print("  Directory: " + str(i))

        #Go through all the files in the directory and if they end with the required suffix then do a hash on them and store the value
        for i in files:
            if DEBUG:
                print("  Files: " + str(i))

            if i.endswith(suffix):

                #Create the full file name
                if root.endswith("/"):
                    ffn = root + i
                else:
                    ffn=root+"/" + i

                #Get file size
                filesize=os.stat(ffn).st_size

                try:
                    with open(ffn) as f:
                        hash = hashlib.md5(f.read()).hexdigest()
                    print(str(hash) + " " + str(filesize) + " " + ffn)
                    f.closed
                except:
                    print("  Unable to open " + ffn + "  ", sys.exc_info()[0], sys.exc_info()[1])


######################
###
### Program start
###
######################

# Get the arguments from the command line
parser = argparse.ArgumentParser(description="Catalogs all the files on the system with a cryptographic hash.")
parser.add_argument('--suffix',help="Only look at files that end in this. (i.e. \".png\")",nargs=1,action="store")
parser.add_argument('--start',help="The directory to start from, other than \"/\"",nargs=1,action="store")
parser.add_argument('--debug',help="Turn on debugging",action="store_true")
args=parser.parse_args()

DEBUG=False

try:
    if args.suffix[0] != "":
        suffix=args.suffix[0]
except:
    suffix=""

try:
    if args.start[0] != "":
        startdir=args.start[0]
except:
    startdir="/"


if args.debug:
    DEBUG=True
    print("Debugging is enabled.")


walkFiles(DEBUG,startdir,suffix)



