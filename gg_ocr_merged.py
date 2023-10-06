#!/usr/bin/env python
import argparse, re
from pathlib import Path
from os import listdir, makedirs, rename
from os.path import isfile, join, exists
from PIL import Image, ImageDraw

import matplotlib.pyplot as plt
from skimage import data
from skimage import color, morphology
import numpy as np
from skimage.segmentation import flood, flood_fill

if not exists("ocr_result"):
    makedirs("ocr_result")

root_path = "Tap_04_Thanh_N_Ceclilia_Va_Mc_S_Lawrence_Saint_Cecilia_and_Pastor_Lawrence_White_Saint_and_Black_Pastor_2023_HDVietSub"
images_combine = 50
image_width = 1280
image_padding = 100
ultrasound=80 
center_threshold = 0.4
step = 3



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



def detect_document(path, database, detect_line = False, center = True):
    print("start_ocr_merged_image")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    print("got response")

    breaks = vision.TextAnnotation.DetectedBreak.BreakType

    for i in range(len(database)):
        database[i]["para"] = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:

            for paragraph in block.paragraphs:

                vertices = [ [vertex.x,vertex.y] for vertex in paragraph.bounding_box.vertices ]

                # Get start and end symbols coordinate
                start = paragraph.words[0].symbols[0].bounding_box.vertices[0]
                start_b = paragraph.words[0].symbols[0].bounding_box.vertices[3]
                end = paragraph.words[-1].symbols[-1].bounding_box.vertices[1]
                end_b = paragraph.words[-1].symbols[-1].bounding_box.vertices[2]

                # Get para text
                para = ""
                for word in paragraph.words:
                    for symbol in word.symbols:
                        para += symbol.text
                        if symbol.property.detected_break.type == breaks.SPACE:
                            para += ' '
                        if symbol.property.detected_break.type == breaks.SURE_SPACE:
                            para += ' '
                        if symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                            para += "\n"
                        if symbol.property.detected_break.type == breaks.LINE_BREAK:
                            # lines.append(line)
                            para += "\n"
                para = clear_text(para)

                for i in range(len(database)):
                    if is_point_in_box(vertices[0], database[i]["box"]) and is_point_in_box(vertices[2], database[i]["box"] ) :
                        database[i]["para"] += [{"text": para, "box": [vertices[0][0],vertices[0][1],vertices[2][0],vertices[2][1]], "start": start, "end": end, "start_b": start_b, "end_b": end_b, 
                                        "reg_box": [start.y,start.x,start_b.y,start_b.x+ultrasound ], "raw":paragraph }]
    i=0
    while i<len(database):
        if database[i]["para"] == []:
            database[i]["para"] = [{"text": ""}]

            Path(join(root_path, "warning cant ocr")).mkdir(parents=True, exist_ok=True)
            rename(join(root_path ,database[i]["name"]) , join(root_path, "warning cant ocr" ,database[i]["name"] ) )
            print("Warning: {} file not recognize text -->  moving 'warning cant ocr' folders".format(database[i]["name"]))
            del database[i]
        else:
            i+=1

    # Get lines of paras
    if detect_line:
        for i in range(len(database)):
            database[i]["lines"], database[i]["lines_box"] = get_lines_of_paragraph( database[i]["para"])

        return database


    for i in range(len(database)):
        paras = database[i]["para"]
        lines = []
        twords = [w.__dict__ for p in paras for w in p["raw"].words ]
        for i in range(len(twords)):
            twords[i]['box'] = get_box(twords[i]["_pb"].bounding_box.vertices)

        min_height = min([abs(w["box"][1]-w["box"][3]) for w in twords])
        
        while len(twords) > 0:
            sample = twords[0]
            line = [twords[0]]
            del twords[0]
            i = 0
            while i < len(twords):
                if abs(sample["box"][1] - twords[i]["box"][1]) < min_height*2//3:
                    line+=[twords[i]]
                    del twords[i]
                else:
                    i+=1
            lines+=[line]
        # Sort theo thu tu
        lines = sorted(lines, key=lambda line: line[0]["box"][1])
        for i in range(len(lines)):
            lines[i] = sorted(lines[i], key=lambda w: w["box"][0])
        
        text = ""
        for line in lines:
            for w in line:
                temp = ""
                for symbol in w["_pb"].symbols:
                    temp += symbol.text
                    if symbol.property.detected_break.type_ == breaks.SPACE:
                        temp += ' '
                    if symbol.property.detected_break.type_ == breaks.SURE_SPACE:
                        temp += ' '
                    if symbol.property.detected_break.type_ == breaks.EOL_SURE_SPACE:
                        temp += "\n"
                    if symbol.property.detected_break.type_ == breaks.LINE_BREAK:
                        # lines.append(line)
                        temp += "\n"
                text += temp
        text = clear_text(text)

        database[i]["text"] = text 

        print(text)

    # #Draw image
    # for datab in range(len(database)):
    #     for t in database[datab]["lines_box"]:
    #         img1 = ImageDraw.Draw(new_image)
    #         img1.rectangle(t , outline ="blue")
    # new_image.show() 

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
    f= open("ocr_raw_result.txt", "r", encoding= "utf8")
    already_ocr = f.read().split("\n")
    already_ocr = [g.split("\t")[0].replace("ocr_result\\","") for g in already_ocr]
    f.close()
except:
    print("Warning: Can't find ocr_raw_result.txt")
    already_ocr = []

i=0
while i<len(listfile):
    temp = join(root_path, listfile[i])
    temp = temp[:temp.rfind(".")] + ".txt"
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

    # detect lines making lines masking image
    lines_database = detect_document(join( "merged_image.jpg" ), image_database, detect_line = True)
    lines_mask_img = Image.new('RGB',(image_width, total_height), (0,0,0))
    for d in lines_database:
        for box in d["lines_box"]:
            img2 = ImageDraw.Draw(lines_mask_img)
            img2.rectangle([box[0],box[1],box[2],box[3]] , fill = "white", outline ="white")
    lines_mask_img = np.array(lines_mask_img)[:,:,0]
    
    # aply mask and make delete img 
    # binary_img = Image.open("merged_image.jpg")
    binary_img = np.array(new_image)[:,:]
    delete_img = np.zeros_like(binary_img)
    delete_img[np.logical_and(binary_img,np.invert(lines_mask_img))] = 255
    #Flood delete img to actual remove object
    for i in range(0,binary_img.shape[0],step):
        for j in range(0,binary_img.shape[1],step): 
            if delete_img[i][j]==255 and binary_img[i][j]>100:
                true_binary_img = binary_img>100
                flood_img = flood(true_binary_img, (i,j))
                binary_img[flood_img] = 0

    new_image = Image.fromarray(binary_img, 'L')
    new_image.save("merged_image.jpg","JPEG")

    result = detect_document(join( "merged_image.jpg" ), image_database)

    # new_image.show()

    # Write to files:
    fa = open("ocr_raw_result.txt", "a", encoding = "utf8")
    for para in result:
        path = join("ocr_result", root_path ,   para["name"][:para["name"].rfind(".")]+".txt" )
        Path(path[:path.rfind("\\")]).mkdir(parents=True, exist_ok=True)
        f = open(path, "w", encoding = "utf8")
        try:
            f.write(para["text"])
        except:
            pass
        f.close()

        # print(para.keys())
        # print(para["name"])
        # fa.write( path + "\t" + str(para["text"]) )
        # fa.write( "\n" )

    fa.close()






# print(listfile)