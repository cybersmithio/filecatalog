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

#https://docs.python.org/3.3/library/json.html#module-json
import json

import re

def walkFiles(DEBUG,startdir,suffix,outputfilename):
    if outputfilename == "":
        OUTPUTFILE=False
    else:
        OUTPUTFILE=True

    count=0
    if OUTPUTFILE:
        outf=open(outputfilename,"w+")
    output=[]
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

            if len(re.findall(str(suffix)+"$", i, flags=re.IGNORECASE)) > 0:

                #Create the full file name
                if root.endswith("/"):
                    ffn = root + i
                else:
                    ffn=root+"/" + i

                filename=i
                #Get file size
                filesize=os.stat(ffn).st_size

                try:
                    with open(ffn) as f:
                        hash = hashlib.md5(f.read()).hexdigest()
                    output.append({"hash": hash, "size": filesize, "name": filename, "fullpath": ffn})
                    if DEBUG:
                        print(str(hash) + " " + str(filesize) + " " + ffn)
                    f.closed
                    count=count+1
                    sys.stdout.write("\rFiles matching: "+str(count)+"    ")
                    sys.stdout.flush()
                except:
                    print("  Unable to open " + ffn + "  ", sys.exc_info()[0], sys.exc_info()[1])
    #Put out a new line after the "Files matching" status line
    print("\n")
    if OUTPUTFILE:
        json.dump(output, outf)
        outf.closed
    else:
        print(json.dumps(output))
    print("Total files found and catalogued: "+str(count))

def compareFiles(DEBUG, file1, file2):
    print("Comparing these two files: "+str(file1)+" and "+str(file2))

    #Read file 1
    if DEBUG:
        print("Reading "+str(file1))
    try:
        fp1=open(file1,"r")
    except:
        print("Unable to open "+str(file1), sys.exc_info()[0], sys.exc_info()[1])
        return(False)

    #Parse JSON from file 1
    try:
        file1json=json.load(fp1)
    except:
        print("Unable to load json "+str(file1), sys.exc_info()[0], sys.exc_info()[1])

    #Read file 2
    if DEBUG:
        print("Reading "+str(file2))
    try:
        fp2=open(file2,"r")

    except:
        print("Unable to open "+str(file2), sys.exc_info()[0], sys.exc_info()[1])
        return(False)

    #Parse JSON from file 2
    try:
        file2json=json.load(fp2)
    except:
        print("Unable to load json "+str(file2), sys.exc_info()[0], sys.exc_info()[1])

    DIFF=False
    #The number of files missing from catalog 1
    missing1=0
    #The number of files missing from catalog 2
    missing2=0

    #The size of the files missing from catalog 1 that are in catalog 2
    sizeofmissing1=0
    #The size of the files missing from catalog 2 that are in catalog 1
    sizeofmissing2=0

    #Iterate through file 2 and see if the same files are in file 1
    for line in file1json:
        if DEBUG:
            print("\n\nRead line " + str(line))
            print("File name is: " + str(line['name']))
            print("File size is: " + str(line['size']))
            print("File hash is: " + str(line['hash']))
        FOUND=False
        for x in file2json:
            if (line['hash'] == x['hash']) and (line['size'] == x['size']):
                if DEBUG:
                    print("Found a match")
                FOUND=True
        if not FOUND:
            print("File "+str(line['name'])+" is in "+str(file1)+" but not in "+str(file2))
            DIFF=True
            missing2=missing2+1
            sizeofmissing2=sizeofmissing2+int(line['size'])

    #Iterate through file 2 and see if the same files are in file 1
    for line in file2json:
        if DEBUG:
            print("\n\nRead line " + str(line))
            print("File name is: " + str(line['name']))
            print("File size is: " + str(line['size']))
            print("File hash is: " + str(line['hash']))
        FOUND=False
        for x in file1json:
            if (line['hash'] == x['hash']) and (line['size'] == x['size']):
                if DEBUG:
                    print("Found a match")
                FOUND=True
        if not FOUND:
            print("File "+str(line['name'])+" is in "+str(file2)+" but not in "+str(file1))
            DIFF=True
            missing1=missing1+1
            sizeofmissing1=sizeofmissing1+int(line['size'])


    print("Summary of findings:")
    if not DIFF:
        print("There were no differences found in the file catalogs.")
    if missing1 > 0:
        print("Files missing from catalog 1: "+str(missing1))
        print("The size in bytes of the files missing from catalog 1: "+str(sizeofmissing1))
    if missing2 > 0:
        print("Files missing from catalog 2: "+str(missing2))
        print("The size in bytes of the files missing from catalog 2: "+str(sizeofmissing2))


    fp1.close()
    fp2.close()



######################
###
### Program start
###
######################

# Get the arguments from the command line
parser = argparse.ArgumentParser(description="Catalogs all the files on the system with a cryptographic hash.")
parser.add_argument('--suffix',help="Only look at files that end in this. (i.e. \".png\")",nargs=1,action="store")
parser.add_argument('--start',help="The directory to start from, other than \"/\"",nargs=1,action="store")
parser.add_argument('--compare',help="Take two output files and compare them",nargs=2,action="store")
parser.add_argument('--output',help="The output JSON file",nargs=1,action="store")
parser.add_argument('--finddups',help="Highlights any duplicate files, based on hash and file size",action="store_true")
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

try:
    if args.output[0] != "":
        outputfile=str(args.output[0])
except:
    outputfile=""



try:
    if args.compare[0] != "":
        COMPARE=True
except:
    COMPARE=False

if COMPARE:
    compareFiles(DEBUG,str(args.compare[0]),str(args.compare[1]))
    exit(0)

walkFiles(DEBUG,startdir,suffix,outputfile)



