#!/usr/bin/env python
import argparse
from pathlib import Path
from os import listdir, makedirs, rename
from os.path import isfile, join, exists

root_path = "ocr_result"
listfolder = [f for f in listdir(root_path) if not isfile(join(root_path,f) ) ]


for fol in listfolder:
	print("write {}.srt".format(fol))
	srt_file = open(join(root_path, fol+".srt") , "w" , encoding = "utf8")
	listfiles = [f for f in listdir(join(root_path, fol)) if isfile(join(root_path, fol, f)) and ".txt" in f ]
	i=1
	for file in listfiles:
		f = open(join(root_path, fol, file), "r", encoding = "utf8")
		data = f.read()
		f.close()

		def rreplace(s, old, new):
			li = s.rsplit(old, 1)
			return new.join(li)

		time = file.replace(".txt","")
		time = time.replace("_",":")
		time = time.split("::")
		time[0] = rreplace(time[0], ":" , "," )
		time[1] = rreplace(time[1], ":" , "," )

		srt_file.write("{}\n{} --> {}\n{}\n\n".format( str(i), time[0], time[1], data  ))

		i+=1

	srt_file.close()
