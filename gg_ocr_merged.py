#!/usr/bin/env python
import argparse, re
from pathlib import Path
from os import listdir, makedirs, rename
from os.path import isfile, join, exists
from PIL import Image, ImageDraw 
if not exists("ocr_result"):
    makedirs("ocr_result")

root_path = "Tap_06_Thanh_N_Ceclilia_Va_Mc_S_Lawrence_Saint_Cecilia_and_Pastor_Lawrence_White_Saint_and_Black_Pastor_2023_HDVietSub"
images_combine = 50
image_width = 1280
image_padding = 100
ultrasound=80 



def is_point_in_box(point, box):
    if ( box[0] <= point[0] <= box[2] ) and ( box[1] <= point[1] <= box[3] ):
        return True
    else:
        return False

def clear_text(p):
    if p=="":
        return ""
    if p[0]=="\n":
        p=p[1]
    if p[-1]=="\n":
        p = p[:-1]
    p = re.sub(r"([a-zA-Z0-9]*[^ a-zA-Z0-9]+[a-zA-Z0-9]*)\-([a-zA-Z0-9]*[^ a-zA-Z0-9]+[a-zA-Z0-9]*)",r"\1 \2",p)
    p = re.sub(r"\n+",r"\\n",p)
    return p

def detect_document(path, database):
    print("start_ocr_merged_image")
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    with open(path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    breaks = vision.TextAnnotation.DetectedBreak.BreakType

    for page in response.full_text_annotation.pages:
        for block in page.blocks:

            for paragraph in block.paragraphs:

                vertices = [ [vertex.x,vertex.y] for vertex in paragraph.bounding_box.vertices ]

                # #Draw image
                # img1 = ImageDraw.Draw(new_image)
                # temp = [vertices[0][0],vertices[0][1],vertices[2][0],vertices[2][1]]
                # img1.rectangle([min([temp[0],temp[2]]),min([temp[1],temp[3]]),max([temp[0],temp[2]]),max([temp[1],temp[3]])] , outline ="red")

                para = ""
                # Get start and end symbols coordinate
                start = paragraph.words[0].symbols[0].bounding_box.vertices[0]
                start_b = paragraph.words[0].symbols[0].bounding_box.vertices[3]
                end = paragraph.words[-1].symbols[-1].bounding_box.vertices[1]
                end_b = paragraph.words[-1].symbols[-1].bounding_box.vertices[2]
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
                        database[i]["para"] += [{"text": para, "box": vertices, "start": start, "end": end, "start_b": start_b, "end_b": end_b, 
                                        "reg_box": [start.y,start.x,start_b.y,start_b.x+ultrasound ] }]
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

    # Combine paras to text
    for i in range(len(database)):
        paras = database[i]["para"]
        text = ""
        min_height = min([abs(t["start_b"].y-t["start"].y) for t in paras])
        mouse_y = min([t["start"].y for t in paras]) +min_height//4
        mouse_x = 0
        mouse_height = min_height//2
        if mouse_height == 0: mouse_height= ultrasound//2
        # Timf para cungf line gan nhat <(")
        while mouse_y < database[i]["box"][3] and len(paras)!=0:
            while mouse_x < image_width:
                g=0
                while g< len(paras):
                    if is_point_in_box([mouse_y,mouse_x], paras[g]["reg_box"] ) or is_point_in_box([mouse_y+mouse_height,mouse_x], paras[g]["reg_box"] ):
                        text += paras[g]["text"] + " "
                        mouse_y = paras[g]["end"].y
                        mouse_x = paras[g]["end"].x
                        del paras[g]
                    else:
                        g+=1
                mouse_x += ultrasound
                # print(mouse_y,mouse_x)
            mouse_y+=mouse_height*3//2
            mouse_x=0
            text+="\n"
        
        text = clear_text(text)
        database[i]["text"] = text 
        print(text)
   
    # new_image.show() 

    return database

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )



# [END vision_text_detection]

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

    new_image.save("merged_image.jpg","JPEG")
    result = detect_document(join( "merged_image.jpg" ), image_database)


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

        fa.write( path + "\t" + str(para["text"]) )
        fa.write( "\n" )

    fa.close()





# print(listfile)