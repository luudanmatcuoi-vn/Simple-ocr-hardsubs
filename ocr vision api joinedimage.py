#!/usr/bin/env python

# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import argparse, threading, time, sys
from pathlib import Path
from os import listdir, system
from os.path import isfile, join
import base64
from google.cloud import vision

lock = threading.Lock()
max_threads = 1
padding_line_slice = 6

def detect_text(path):
    print("start ocr "+path)
    client = vision.ImageAnnotatorClient()
    # [START vision_python_migration_text_detection]
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    print("Got response, progressing result...")

    raw_result = []
    for i in range(1,len(texts)):
        vertices = [ { "x":v.x , "y":v.y } for v in texts[i].bounding_poly.vertices ]
        # Get break_detected
        def get_break_type():
            breaks = vision.TextAnnotation.DetectedBreak.BreakType
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            if texts[i].bounding_poly.vertices == word.bounding_box.vertices:
                                if word.symbols[-1].property.detected_break.type == breaks.SPACE:
                                    break_type = " "
                                elif word.symbols[-1].property.detected_break.type == breaks.SURE_SPACE:
                                    break_type = " "
                                elif word.symbols[-1].property.detected_break.type == breaks.EOL_SURE_SPACE:
                                    break_type = " "
                                elif word.symbols[-1].property.detected_break.type == breaks.LINE_BREAK:
                                    break_type = " "
                                elif word.symbols[-1].property.detected_break.type == breaks.HYPHEN:
                                    break_type = "-"
                                else:
                                    break_type = ""
                                return break_type

        break_type = get_break_type()

        res={
            "text" :       texts[i].description,
            "vertices" :   vertices,
            "break_type" : break_type
            }
        raw_result += [res]


    def is_in_line(vertices, y ):
        height = abs(vertices[0]["y"]-vertices[2]["y"])
        if (vertices[0]["y"]-height//padding_line_slice - y)*(vertices[2]["y"]+-height//padding_line_slice - y)<=0:
            return True
        else:
            return False

    def get_center_y(vertices):
        return (vertices[0]["y"]+vertices[2]["y"])//2

    def add_text(data,add):
        data["line"] += [add]
        data["line"] = sorted(data["line"], key=lambda d: d['vertices'][0]["x"])
        return data

    result = []
    global is_found_ids
    is_found_ids = False
    for te in raw_result:
        id_list = [k["id"] for k in result]
        for ids in range(len(id_list)):
            if is_in_line(te["vertices"], id_list[ids]):
                is_found_ids = True
                ids_found = ids
                break
            else:
                is_found_ids = False
        if is_found_ids:
            result[ids_found] = add_text(result[ids_found],te)
        else:
            temp = {"id": get_center_y(te["vertices"]), "line":[te]}
            result += [temp]

    result = sorted(result, key=lambda d: d['id'])

    result = "\n".join(["".join(t["text"]+t["break_type"] for t in g["line"]) for g in result])
    # result = result.replace()

    # Write to files:
    path = "TXTResults\\" + path[:path.rfind(".")]+".txt"
    path = path.replace("ImagesJoined\\","")
    Path(path[:path.rfind("\\")]).mkdir(parents=True, exist_ok=True)
    f = open(path, "w", encoding = "utf8")
    try:
        f.write(result)
    except:
        pass
    f.close()

    # write_ocr_raw_result( path + "\t" + str(result) )
    return result

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    # [END vision_python_migration_text_detection]

# root_path = root_path.split("\\")[-1]

# listfile = [f for f in listdir(join("cleared_image",root_path)) if isfile(join("cleared_image",root_path, f) ) and ".txt" not in f and ".xml" not in f and ".sup" not in f]

listfile = [f for f in listdir(join("ImagesJoined")) if isfile(join("ImagesJoined", f) ) and ".txt" not in f and ".xml" not in f and ".sup" not in f]

# f= open("ocr_raw_result.txt", "r", encoding= "utf8")
# already_ocr = f.read().split("\n")
# already_ocr = [g.split("\t")[0].replace("ocr_result\\","") for g in already_ocr]
# f.close()



# threads = []
# for file in listfile:
#     temp = join("ImagesJoined", file)
#     temp = temp[:temp.rfind(".")] + ".txt"
#     if "already_ocr" not in globals() or temp in already_ocr:

#         while True:
#             threads = [t for t in threads if t.is_alive()]
#             print(len(threads))
#             if len(threads) > max_threads:
#                 time.sleep(2)
#             else:
#                 break

#         th = threading.Thread(target=detect_text, args=( join("ImagesJoined", file), ) )
#         threads.append(th)
#         th.start()

total_result = ""
for file in listfile:
    temp = join("ImagesJoined", file)
    temp = temp[:temp.rfind(".")] + ".txt"
    if "already_ocr" not in globals() or temp in already_ocr:
        total_result += detect_text(join("ImagesJoined", file))
        total_result += "\n"

f = open(join("TXTResults", "join_txt_results.txt"), "w", encoding = "utf8")
try:
    f.write(total_result)
except:
    pass


print("done")
system('pause')