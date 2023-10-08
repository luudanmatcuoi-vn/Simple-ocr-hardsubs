#!/usr/bin/env python

# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import argparse, threading, time, sys
from pathlib import Path
from os import listdir, system
from os.path import isfile, join

lock = threading.Lock()
max_threads = 40

# def write_ocr_raw_result(res):
#     lock.acquire() # thread blocks at this line until it can obtain lock

#     f = open("ocr_raw_result.txt", "a", encoding = "utf8")
#     f.write( res + "\n")
#     f.close()

#     lock.release()

def detect_text(path):
    print("start thread")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    # [START vision_python_migration_text_detection]
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    result = []
    for text in texts:
        res= [f'\n"{text.description}"']
        vertices = [
            f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
        ]
        res += ["bounds: {}".format(";".join(vertices))]
        result += [res]

    print(result)

    # Write to files:
    path = "ocr_result\\" + path[:path.rfind(".")]+".txt"
    path = path.replace("cleared_image\\","")
    Path(path[:path.rfind("\\")]).mkdir(parents=True, exist_ok=True)
    f = open(path, "w", encoding = "utf8")
    try:
        f.write(texts[0].description)
    except:
        pass
    f.close()

    # write_ocr_raw_result( path + "\t" + str(result) )
    return True

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    # [END vision_python_migration_text_detection]

## Detect root_path
print("\nDrag and drop A folder contain images to start clean.\nNote: Folder must have the same directory with python script\n")

if len(sys.argv)==1:
    root_path = input("folder :") 
else:
    # args.folder = sorted(args.folder)
    root_path = str(sys.argv[1])
    if root_path[0]=="'": root_path = root_path[1:]
    if root_path[-1]=="'": root_path = root_path[:-1]

root_path = root_path.split("\\")[-1]

listfile = [f for f in listdir(join("cleared_image",root_path)) if isfile(join("cleared_image",root_path, f) ) and ".txt" not in f and ".xml" not in f and ".sup" not in f]

f= open("ocr_raw_result.txt", "r", encoding= "utf8")
already_ocr = f.read().split("\n")
already_ocr = [g.split("\t")[0].replace("ocr_result\\","") for g in already_ocr]
f.close()

threads = []

for file in listfile:
    temp = join("cleared_image",root_path, file)
    temp = temp[:temp.rfind(".")] + ".txt"
    if temp in already_ocr:
        pass
    else:
        while True:
            threads = [t for t in threads if t.is_alive()]
            print(len(threads))
            if len(threads) > max_threads:
                time.sleep(2)
            else:
                break

        th = threading.Thread(target=detect_text, args=( join("cleared_image",root_path, file), ) )
        threads.append(th)
        th.start()

print("done")
system('pause')