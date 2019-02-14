#!/usr/bin/env python3

import os
import sys
import argparse
import mysql.connector
import lzma
import socket
import subprocess

###########################################################
def systemCheck(cmd):
    sys.stderr.write("Executing:" + cmd + " on " + socket.gethostname() + "\n")
    sys.stderr.flush()

    subprocess.check_call(cmd, shell=True)
###########################################################

oparser = argparse.ArgumentParser(description="Hello")
oparser.add_argument('--dir', dest='dir', help='Data directory', required=True)
options = oparser.parse_args()

mydb = mysql.connector.connect(
    host="localhost",
    user="paracrawl_user",
    passwd="paracrawl_password",
    database="paracrawl",
    charset='utf8'
)

mycursor = mydb.cursor()

for fileName in os.listdir(options.dir):
    if fileName[-8:] != ".text.xz":
        continue

    filePrefix = fileName[:-8]
    fileId = int(filePrefix)
    translatedFile = filePrefix + ".trans"
    #print("fileName", fileName, filePrefix, fileName[-8:], translatedFile)

    # translated already?
    if os.path.isfile(translatedFile):
        continue

    # what language is it in?
    sql = "SELECT lang FROM document WHERE id = %s"
    val = (fileId,)
    mycursor.execute(sql, val)
    res = mycursor.fetchone()
    assert(res != None)
    lang = res[0]
    print("fileName", fileName, filePrefix, fileName[-8:], translatedFile, lang)

    if lang != "fr":
        continue

    txtPath = options.dir + "/" + fileName
    with lzma.open(txtPath, 'rt') as f:
        txt = f.read()
    #print("txt", txt)

    #cmd = "xzcat " + txtPath + " | ~/workspace/github/mosesdecoder/bin/moses2 -f /home/hieu/workspace/experiment/issues/paracrawl/fr-en/smt-dir/model/moses.bin.ini.1"
    #systemCheck(cmd)
    proc = subprocess.Popen(["/home/hieu/workspace/github/mosesdecoder/bin/moses2",
                             "-f",
                             "/home/hieu/workspace/experiment/issues/paracrawl/fr-en/smt-dir/model/moses.bin.ini.1"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write("matthew\n".encode('utf-8'))
    proc.stdin.write("mark\n".encode('utf-8'))
    proc.stdin.write("luke\n".encode('utf-8'))
    proc.stdin.close()

    while proc.returncode is None:
        proc.poll()

    print("I got back from the program this:\n{0}".format(proc.stdout.read()))

