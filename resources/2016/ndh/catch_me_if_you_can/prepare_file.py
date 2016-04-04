#!/usr/bin/env python2
from os.path import join
from os import listdir

working_dir = "working"

folder = []
files1 = []
files2 = []
for i in listdir(working_dir):
    folder.append(i)

folder.sort()
for i in folder:
    if int(i) % 2:
        files1.append(i)
    else:
        files2.append(i)

#reorder the blob
files1.sort()
files2.sort()

# create the files1
with open("files1.ods", "wb") as final_files1:

    # clean the sample
    for i in files1:
        final_files1.write(open(join(working_dir, i)).read(0x708))


# create the files2
with open("files2.ods", "wb") as final_files2:

    # clean the sample
    for i in files2:
        final_files2.write(open(join(working_dir, i)).read(0x708))

