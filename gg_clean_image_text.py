#!/usr/bin/env python

# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import sys, re, threading
from pathlib import Path
from os import listdir, makedirs, rename, system
from os.path import isfile, join, exists
from PIL import Image, ImageDraw

import matplotlib.pyplot as plt
from skimage import data
from skimage import color, morphology
import numpy as np
from skimage.segmentation import flood, flood_fill

image_width = 1280                  # rescale before ping gg cloud
images_combine = 50                 # number of image combined
image_padding = 100                 # padding between image
ultrasound=80                       # just for fun :v      
center = True                       # is subtitle always in center position ? 
center_threshold = 0.6              # threshold to detect are lines center or not
step = 5                            # smaller can clear object better but slower... not working
max_threads = 30                    # number of threads... not working


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

Path("cleared_image").mkdir(parents=True, exist_ok=True)

def is_point_in_box(point, box):
    if ( box[0] <= point[0] <= box[2] ) and ( box[1] <= point[1] <= box[3] ):
        return True
    else:
        return False
def expand_box(box,step):
    return [box[0]-step[0],box[1]-step[1],box[2]+step[0],box[3]+step[1]]
def get_box(ver):
    return [ver[0].x, ver[0].y, ver[2].x, ver[2].y]
def clear_text(p):
    if p=="":
        return ""
    if p[0]=="\n":
        p=p[1:]
    if p[-1]=="\n":
        p = p[:-1]
    p = re.sub(r"([a-zA-Z0-9]*[^ a-zA-Z0-9]+[a-zA-Z0-9]*)\-([a-zA-Z0-9]*[^ a-zA-Z0-9]+[a-zA-Z0-9]*)",r"\1 \2",p)
    p = re.sub(r"\n+",r"\\n",p)
    return p

def get_lines_of_paragraph(paras, center = True):
    lines = []
    words = [w.__dict__ for p in paras for w in p["raw"].words ]
    for i in range(len(words)):
        # box = words[i].box = get_box(words[i].bounding_box.vertices)
        box = words[i]['box'] = get_box(words[i]["_pb"].bounding_box.vertices)

    lines = []

    min_height = min([abs(w["box"][1]-w["box"][3]) for w in words])
    
    while len(words) > 0:
        sample = words[0]
        line = [words[0]["box"]]
        del words[0]
        i = 0
        while i < len(words):
            if abs(sample["box"][1] - words[i]["box"][1]) < min_height*2//3:
                line+=[words[i]["box"]]
                del words[i]
            else:
                i+=1
        lines+=[line]
    # Sort word theo thu tu
    lines = sorted(lines, key=lambda line: line[0][1])
    for i in range(len(lines)):
        lines[i] = sorted(lines[i], key=lambda w: w[0])
    

    if center == True:
        i=0
        while i<len(lines):
            if (lines[i][0][0]-image_width//2)*(lines[i][-1][2]-image_width//2)>0 and abs(lines[i][0][0]-image_width//2)>image_width//2*center_threshold and abs(lines[i][0][0]-image_width//2)>image_width//2*center_threshold:
                print("remove ", lines[i])
                # for g in range(len(lines[i])):
                #     img1 = ImageDraw.Draw(new_image)
                #     img1.rectangle(lines[i][g] , outline ="red")
                del lines[i]
            else:
                i+=1

    # Create line_box
    line_box = []
    for l in lines:
        temp = [l[0][0],min([t[1] for t in l]) ,l[-1][2],max([t[3] for t in l]) ]
        temp = expand_box(temp, [1,3])
        line_box += [temp]

    if center:
        for i in range(len(line_box)):
            temp = max([abs(line_box[i][0]-image_width//2),abs(line_box[i][2]-image_width//2)])
            line_box[i][0] = image_width//2-temp
            line_box[i][2] = image_width//2+temp
    
    # print(lines)
    return lines, line_box



def detect_document_lines(path, database, center = True):
    print("start_ping_gg_cloud_vision_api")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    print("got response")

    breaks = vision.TextAnnotation.DetectedBreak.BreakType

    # for i in range(len(database)):
    #     database[i]["para"] = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:

            for paragraph in block.paragraphs:

                vertices = [ [vertex.x,vertex.y] for vertex in paragraph.bounding_box.vertices ]

                # Get start and end symbols coordinate
                start = paragraph.words[0].symbols[0].bounding_box.vertices[0]
                start_b = paragraph.words[0].symbols[0].bounding_box.vertices[3]
                end = paragraph.words[-1].symbols[-1].bounding_box.vertices[1]
                end_b = paragraph.words[-1].symbols[-1].bounding_box.vertices[2]

                # # Get para text
                # para = ""
                # for word in paragraph.words:
                #     for symbol in word.symbols:
                #         para += symbol.text
                #         if symbol.property.detected_break.type == breaks.SPACE:
                #             para += ' '
                #         if symbol.property.detected_break.type == breaks.SURE_SPACE:
                #             para += ' '
                #         if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                #             para += "\n"
                #         if symbol.property.detected_break.type == breaks.LINE_BREAK:
                #             # lines.append(line)
                #             para += "\n"
                # para = clear_text(para)

                for i in range(len(database)):
                    if is_point_in_box(vertices[0], database[i]["box"]) and is_point_in_box(vertices[2], database[i]["box"] ) :
                        database[i]["para"] += [{ "box": [vertices[0][0],vertices[0][1],vertices[2][0],vertices[2][1]], 
                                                "start": start, "end": end, "start_b": start_b, "end_b": end_b, 
                                                "raw":paragraph }]
                        # database[i]["para"] += [{ "box": [vertices[0][0],vertices[0][1],vertices[2][0],vertices[2][1]], 
                        #                 "start": start, "end": end, "start_b": start_b, "end_b": end_b, 
                        #                 "reg_box": [start.y,start.x,start_b.y,start_b.x+ultrasound ], "raw":paragraph }]

    i=0
    while i<len(database):
        if database[i]["para"] == []:
            # database[i]["para"] = [{"text": ""}]

            Path(join(root_path, "warning cant ocr")).mkdir(parents=True, exist_ok=True)
            rename(join(root_path ,database[i]["name"]) , join(root_path, "warning cant ocr" ,database[i]["name"] ) )
            print("Warning: {} file not recognize text -->  moving 'warning cant ocr' folders".format(database[i]["name"]))
            del database[i]
        else:
            i+=1

    # Get lines of paras

    for i in range(len(database)):
        database[i]["lines"], database[i]["lines_box"] = get_lines_of_paragraph( database[i]["para"])

    return database

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

# [END vision_text_detection]





def filter_small_object(img):
    image = np.array(img)[:,:,0]
    footprint = morphology.disk(1)
    res = morphology.white_tophat(image, footprint)
    im = Image.fromarray(image - res, 'L')
    return im


listfile = [f for f in listdir(root_path) if isfile(join(root_path, f) ) and ".txt" not in f and ".xml" not in f and ".sup" not in f]

try:
    f= open("previous_cleared_image.txt", "r", encoding= "utf8")
    already_ocr = f.read().split("\n")
    already_ocr = [g.split("\t")[0].replace("ocr_result\\","").replace(".jpg","") for g in already_ocr]
    f.close()
except:
    print("Warning: Can't find previous_cleared_image.txt")
    already_ocr = []

i=0
while i<len(listfile):
    temp = join(root_path, listfile[i])
    temp = temp[:temp.rfind(".")]
    if temp in already_ocr:
        listfile.remove(listfile[i])
    else:
        i+=1

for bl in range(0,len(listfile),images_combine):
    images = []
    images_name = listfile[bl:bl+images_combine]
    for file in images_name:
        images+= [[Image.open(join( root_path, file ))]]
        # Resize and add size
        width , height = images[-1][0].size
        images[-1][0] = images[-1][0].resize((image_width, height*image_width//width))
        images[-1] += [height*image_width//width]

    # Build image and image location
    total_height = sum([g[1] for g in images]) + images_combine*image_padding+10
    new_image = Image.new('RGB',(image_width, total_height), (0,0,0))
    y = 0
    image_database = []
    for i in range(len(images)):
        new_image.paste(images[i][0],(0, y ))
        image_database += [{"id": i, "name": images_name[i], "box":[0,y,1280,y+images[i][1]], "para": [] }]
        y += images[i][1]+image_padding
    
    # Remove dust
    new_image = filter_small_object(new_image)

    new_image.save("merged_image.jpg","JPEG")
    
    org_image = new_image

    # FAST METHOD: detect lines making lines masking image
    lines_database = detect_document_lines(join( "merged_image.jpg" ), image_database, center = center)
    lines_mask_img = Image.new('RGB',(image_width, total_height), (0,0,0))
    for d in lines_database:
        for box in d["lines_box"]:
            img2 = ImageDraw.Draw(lines_mask_img)
            img2.rectangle([box[0],box[1],box[2],box[3]] , fill = "white", outline ="white")
    lines_mask_img = np.array(lines_mask_img)[:,:,0]

    # Get normal size of syl
    syl_size = [abs(syl.bounding_box.vertices[0].x-syl.bounding_box.vertices[1].x) for blockk in lines_database for paraa in blockk["para"] for woo in paraa["raw"].words for syl in woo.symbols]
    mean_syl_size = sum(syl_size)/len(syl_size)
    print("mean_syl_size: ",mean_syl_size)
    # # apply mask and make delete img 
    np_img = np.array(new_image)[:,:]
    # delete_img = np.zeros_like(np_img)
    # delete_img[np.logical_and(np_img,np.invert(lines_mask_img))] = 255


    label_img = label(np_img,connectivity=1)
    delete_img = label_img
    delete_img[np.where(lines_mask_img>100)] = 0
    unique_label = np.unique(delete_img)
    for i in range(len(unique_label)):
        if i==0:continue
        np_img[np.where(label_img == unique_label[i])] = 0

        print(f"{i}/{len(unique_label)}", end = "\r")
    
    # Write to files:
    new_image = Image.fromarray(np_img, 'L')
    Path(join("cleared_image", root_path)).mkdir(parents=True, exist_ok=True)
    for img_db in image_database:
        path = join("cleared_image", root_path , img_db["name"][:img_db["name"].rfind(".")]+".jpg" )
        temp_img = new_image.crop((img_db["box"][0], img_db["box"][1], img_db["box"][2], img_db["box"][3]))
        temp_img.save(path,"JPEG")

        f = open("previous_cleared_image.txt", "a", encoding = "utf8")
        f.write( path + "\t\n")
        f.close()

    # Write cleard merged image for debug purpose
    Path(join("cleared_image", root_path, "debug")).mkdir(parents=True, exist_ok=True)
    path = join("cleared_image", root_path, "debug" , image_database[0]["name"][:img_db["name"].rfind(".")])

    # new_image.save(path+"-cleard.jpg","JPEG")
    lines_mask_img = Image.fromarray(lines_mask_img, 'L')
    # lines_mask_img.save(path+"-lines_mask_img.jpg","JPEG")

    w, h = new_image.size
    debug_img = Image.new('L', (w*3, h))
    debug_img.paste(org_image, (0,0))
    debug_img.paste(lines_mask_img, (w,0))
    debug_img.paste(new_image, (w*2,0))
    debug_img.save(path+"-debug.jpg","JPEG")

system("pause")

# # print(listfile)


