#!/usr/bin/env python
import argparse, re
from pathlib import Path
from os import listdir, makedirs, rename
from os.path import isfile, join, exists

root_path = "ocr_result"
listfolder = [f for f in listdir(root_path) if not isfile(join(root_path,f) ) ]

def clear_text(d):
	d = d.replace("\\n","\\N")
	temp = re.findall(r"^.{0,3}\\N", d)
	if len(temp)>0:
		print(d)
	d = re.sub(r"^.{0,3}\\N",r"",d)

	# if "(" in d or ")" in d:
	# 	print(d)

	# china = re.findall(r'[\u4e00-\u9fff]+', d)
	# if len(china)>0:
	# 	print(d)

	return d

for fol in listfolder:
	print("write {}.srt".format(fol))
	srt_file = open(join(root_path, fol+".srt") , "w" , encoding = "utf8")
	listfiles = [f for f in listdir(join(root_path, fol)) if isfile(join(root_path, fol, f)) and ".txt" in f ]
	i=1
	for file in listfiles:
		f = open(join(root_path, fol, file), "r", encoding = "utf8")
		data = f.read()
		data = clear_text(data)
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

	# break
