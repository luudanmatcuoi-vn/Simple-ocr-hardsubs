
# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import argparse, cv2
from os import rename, system
from os.path import join, split
from pathlib import Path
import re

#crop = "40,550,1200,160"

def no_accent_vietnamese(s):
    s = s
    s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(u'èéẹẻẽêềếệểễ', 'e', s)
    s = re.sub(u'ÈÉẸẺẼÊỀẾỆỂỄ', 'E', s)
    s = re.sub(u'òóọỏõôồốộổỗơờớợởỡ', 'o', s)
    s = re.sub(u'ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ', 'O', s)
    s = re.sub(u'ìíịỉĩ', 'i', s)
    s = re.sub(u'ÌÍỊỈĨ', 'I', s)
    s = re.sub(u'ùúụủũưừứựửữ', 'u', s)
    s = re.sub(u'ƯỪỨỰỬỮÙÚỤỦŨ', 'U', s)
    s = re.sub(u'ỳýỵỷỹ', 'y', s)
    s = re.sub(u'ỲÝỴỶỸ', 'Y', s)
    s = re.sub(u'Đ', 'D', s)
    s = re.sub(u'đ', 'd', s)
    return s

def compound_unicode(unicode_str):
  """
  Chuyển đổi chuỗi Unicode Tổ Hợp sang Unicode Dựng Sẵn
  Edited from: `https://gist.github.com/redphx/9320735`
  """
  unicode_str = unicode_str.replace("\u0065\u0309", "\u1EBB")    # ẻ
  unicode_str = unicode_str.replace("\u0065\u0301", "\u00E9")    # é
  unicode_str = unicode_str.replace("\u0065\u0300", "\u00E8")    # è
  unicode_str = unicode_str.replace("\u0065\u0323", "\u1EB9")    # ẹ
  unicode_str = unicode_str.replace("\u0065\u0303", "\u1EBD")    # ẽ
  unicode_str = unicode_str.replace("\u00EA\u0309", "\u1EC3")    # ể
  unicode_str = unicode_str.replace("\u00EA\u0301", "\u1EBF")    # ế
  unicode_str = unicode_str.replace("\u00EA\u0300", "\u1EC1")    # ề
  unicode_str = unicode_str.replace("\u00EA\u0323", "\u1EC7")    # ệ
  unicode_str = unicode_str.replace("\u00EA\u0303", "\u1EC5")    # ễ
  unicode_str = unicode_str.replace("\u0079\u0309", "\u1EF7")    # ỷ
  unicode_str = unicode_str.replace("\u0079\u0301", "\u00FD")    # ý
  unicode_str = unicode_str.replace("\u0079\u0300", "\u1EF3")    # ỳ
  unicode_str = unicode_str.replace("\u0079\u0323", "\u1EF5")    # ỵ
  unicode_str = unicode_str.replace("\u0079\u0303", "\u1EF9")    # ỹ
  unicode_str = unicode_str.replace("\u0075\u0309", "\u1EE7")    # ủ
  unicode_str = unicode_str.replace("\u0075\u0301", "\u00FA")    # ú
  unicode_str = unicode_str.replace("\u0075\u0300", "\u00F9")    # ù
  unicode_str = unicode_str.replace("\u0075\u0323", "\u1EE5")    # ụ
  unicode_str = unicode_str.replace("\u0075\u0303", "\u0169")    # ũ
  unicode_str = unicode_str.replace("\u01B0\u0309", "\u1EED")    # ử
  unicode_str = unicode_str.replace("\u01B0\u0301", "\u1EE9")    # ứ
  unicode_str = unicode_str.replace("\u01B0\u0300", "\u1EEB")    # ừ
  unicode_str = unicode_str.replace("\u01B0\u0323", "\u1EF1")    # ự
  unicode_str = unicode_str.replace("\u01B0\u0303", "\u1EEF")    # ữ
  unicode_str = unicode_str.replace("\u0069\u0309", "\u1EC9")    # ỉ
  unicode_str = unicode_str.replace("\u0069\u0301", "\u00ED")    # í
  unicode_str = unicode_str.replace("\u0069\u0300", "\u00EC")    # ì
  unicode_str = unicode_str.replace("\u0069\u0323", "\u1ECB")    # ị
  unicode_str = unicode_str.replace("\u0069\u0303", "\u0129")    # ĩ
  unicode_str = unicode_str.replace("\u006F\u0309", "\u1ECF")    # ỏ
  unicode_str = unicode_str.replace("\u006F\u0301", "\u00F3")    # ó
  unicode_str = unicode_str.replace("\u006F\u0300", "\u00F2")    # ò
  unicode_str = unicode_str.replace("\u006F\u0323", "\u1ECD")    # ọ
  unicode_str = unicode_str.replace("\u006F\u0303", "\u00F5")    # õ
  unicode_str = unicode_str.replace("\u01A1\u0309", "\u1EDF")    # ở
  unicode_str = unicode_str.replace("\u01A1\u0301", "\u1EDB")    # ớ
  unicode_str = unicode_str.replace("\u01A1\u0300", "\u1EDD")    # ờ
  unicode_str = unicode_str.replace("\u01A1\u0323", "\u1EE3")    # ợ
  unicode_str = unicode_str.replace("\u01A1\u0303", "\u1EE1")    # ỡ
  unicode_str = unicode_str.replace("\u00F4\u0309", "\u1ED5")    # ổ
  unicode_str = unicode_str.replace("\u00F4\u0301", "\u1ED1")    # ố
  unicode_str = unicode_str.replace("\u00F4\u0300", "\u1ED3")    # ồ
  unicode_str = unicode_str.replace("\u00F4\u0323", "\u1ED9")    # ộ
  unicode_str = unicode_str.replace("\u00F4\u0303", "\u1ED7")    # ỗ
  unicode_str = unicode_str.replace("\u0061\u0309", "\u1EA3")    # ả
  unicode_str = unicode_str.replace("\u0061\u0301", "\u00E1")    # á
  unicode_str = unicode_str.replace("\u0061\u0300", "\u00E0")    # à
  unicode_str = unicode_str.replace("\u0061\u0323", "\u1EA1")    # ạ
  unicode_str = unicode_str.replace("\u0061\u0303", "\u00E3")    # ã
  unicode_str = unicode_str.replace("\u0103\u0309", "\u1EB3")    # ẳ
  unicode_str = unicode_str.replace("\u0103\u0301", "\u1EAF")    # ắ
  unicode_str = unicode_str.replace("\u0103\u0300", "\u1EB1")    # ằ
  unicode_str = unicode_str.replace("\u0103\u0323", "\u1EB7")    # ặ
  unicode_str = unicode_str.replace("\u0103\u0303", "\u1EB5")    # ẵ
  unicode_str = unicode_str.replace("\u00E2\u0309", "\u1EA9")    # ẩ
  unicode_str = unicode_str.replace("\u00E2\u0301", "\u1EA5")    # ấ
  unicode_str = unicode_str.replace("\u00E2\u0300", "\u1EA7")    # ầ
  unicode_str = unicode_str.replace("\u00E2\u0323", "\u1EAD")    # ậ
  unicode_str = unicode_str.replace("\u00E2\u0303", "\u1EAB")    # ẫ
  unicode_str = unicode_str.replace("\u0045\u0309", "\u1EBA")    # Ẻ
  unicode_str = unicode_str.replace("\u0045\u0301", "\u00C9")    # É
  unicode_str = unicode_str.replace("\u0045\u0300", "\u00C8")    # È
  unicode_str = unicode_str.replace("\u0045\u0323", "\u1EB8")    # Ẹ
  unicode_str = unicode_str.replace("\u0045\u0303", "\u1EBC")    # Ẽ
  unicode_str = unicode_str.replace("\u00CA\u0309", "\u1EC2")    # Ể
  unicode_str = unicode_str.replace("\u00CA\u0301", "\u1EBE")    # Ế
  unicode_str = unicode_str.replace("\u00CA\u0300", "\u1EC0")    # Ề
  unicode_str = unicode_str.replace("\u00CA\u0323", "\u1EC6")    # Ệ
  unicode_str = unicode_str.replace("\u00CA\u0303", "\u1EC4")    # Ễ
  unicode_str = unicode_str.replace("\u0059\u0309", "\u1EF6")    # Ỷ
  unicode_str = unicode_str.replace("\u0059\u0301", "\u00DD")    # Ý
  unicode_str = unicode_str.replace("\u0059\u0300", "\u1EF2")    # Ỳ
  unicode_str = unicode_str.replace("\u0059\u0323", "\u1EF4")    # Ỵ
  unicode_str = unicode_str.replace("\u0059\u0303", "\u1EF8")    # Ỹ
  unicode_str = unicode_str.replace("\u0055\u0309", "\u1EE6")    # Ủ
  unicode_str = unicode_str.replace("\u0055\u0301", "\u00DA")    # Ú
  unicode_str = unicode_str.replace("\u0055\u0300", "\u00D9")    # Ù
  unicode_str = unicode_str.replace("\u0055\u0323", "\u1EE4")    # Ụ
  unicode_str = unicode_str.replace("\u0055\u0303", "\u0168")    # Ũ
  unicode_str = unicode_str.replace("\u01AF\u0309", "\u1EEC")    # Ử
  unicode_str = unicode_str.replace("\u01AF\u0301", "\u1EE8")    # Ứ
  unicode_str = unicode_str.replace("\u01AF\u0300", "\u1EEA")    # Ừ
  unicode_str = unicode_str.replace("\u01AF\u0323", "\u1EF0")    # Ự
  unicode_str = unicode_str.replace("\u01AF\u0303", "\u1EEE")    # Ữ
  unicode_str = unicode_str.replace("\u0049\u0309", "\u1EC8")    # Ỉ
  unicode_str = unicode_str.replace("\u0049\u0301", "\u00CD")    # Í
  unicode_str = unicode_str.replace("\u0049\u0300", "\u00CC")    # Ì
  unicode_str = unicode_str.replace("\u0049\u0323", "\u1ECA")    # Ị
  unicode_str = unicode_str.replace("\u0049\u0303", "\u0128")    # Ĩ
  unicode_str = unicode_str.replace("\u004F\u0309", "\u1ECE")    # Ỏ
  unicode_str = unicode_str.replace("\u004F\u0301", "\u00D3")    # Ó
  unicode_str = unicode_str.replace("\u004F\u0300", "\u00D2")    # Ò
  unicode_str = unicode_str.replace("\u004F\u0323", "\u1ECC")    # Ọ
  unicode_str = unicode_str.replace("\u004F\u0303", "\u00D5")    # Õ
  unicode_str = unicode_str.replace("\u01A0\u0309", "\u1EDE")    # Ở
  unicode_str = unicode_str.replace("\u01A0\u0301", "\u1EDA")    # Ớ
  unicode_str = unicode_str.replace("\u01A0\u0300", "\u1EDC")    # Ờ
  unicode_str = unicode_str.replace("\u01A0\u0323", "\u1EE2")    # Ợ
  unicode_str = unicode_str.replace("\u01A0\u0303", "\u1EE0")    # Ỡ
  unicode_str = unicode_str.replace("\u00D4\u0309", "\u1ED4")    # Ổ
  unicode_str = unicode_str.replace("\u00D4\u0301", "\u1ED0")    # Ố
  unicode_str = unicode_str.replace("\u00D4\u0300", "\u1ED2")    # Ồ
  unicode_str = unicode_str.replace("\u00D4\u0323", "\u1ED8")    # Ộ
  unicode_str = unicode_str.replace("\u00D4\u0303", "\u1ED6")    # Ỗ
  unicode_str = unicode_str.replace("\u0041\u0309", "\u1EA2")    # Ả
  unicode_str = unicode_str.replace("\u0041\u0301", "\u00C1")    # Á
  unicode_str = unicode_str.replace("\u0041\u0300", "\u00C0")    # À
  unicode_str = unicode_str.replace("\u0041\u0323", "\u1EA0")    # Ạ
  unicode_str = unicode_str.replace("\u0041\u0303", "\u00C3")    # Ã
  unicode_str = unicode_str.replace("\u0102\u0309", "\u1EB2")    # Ẳ
  unicode_str = unicode_str.replace("\u0102\u0301", "\u1EAE")    # Ắ
  unicode_str = unicode_str.replace("\u0102\u0300", "\u1EB0")    # Ằ
  unicode_str = unicode_str.replace("\u0102\u0323", "\u1EB6")    # Ặ
  unicode_str = unicode_str.replace("\u0102\u0303", "\u1EB4")    # Ẵ
  unicode_str = unicode_str.replace("\u00C2\u0309", "\u1EA8")    # Ẩ
  unicode_str = unicode_str.replace("\u00C2\u0301", "\u1EA4")    # Ấ
  unicode_str = unicode_str.replace("\u00C2\u0300", "\u1EA6")    # Ầ
  unicode_str = unicode_str.replace("\u00C2\u0323", "\u1EAC")    # Ậ
  unicode_str = unicode_str.replace("\u00C2\u0303", "\u1EAA")    # Ẫ
  return unicode_str

parser = argparse.ArgumentParser(description='Throw some video files to create avs script')
parser.add_argument('files', metavar='files', type=Path , nargs='+',
                    help='ass files')
args = parser.parse_args()
args.files = sorted(args.files)

for path in args.files:
    path = str(path)
    # Delete single quote mark
    if path[0]=="'": path = path[1:]
    if path[-1]=="'": path = path[:-1]
    
    # rename, create folder
    path = split(path)
    temp = path[1]
    path = path[0]
    file = temp.replace(" ","_")
    file = compound_unicode(file)
    file = no_accent_vietnamese(file)
    file = "".join([g for g in file if bool(re.search(r"[a-zA-Z0-9\_\.]+", g)) ])
    rename(join(path,temp), join(path,file))
    Path( join(path, file[:file.rfind(".")]) ).mkdir(parents=True, exist_ok=True)
    
    print("Handle file: ",file)
    vid = cv2.VideoCapture(join(path,file))
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    
    if 'crop' in globals():
        pass
    else:
        if height//1 == 1080:
            crop = "40,860,1840,200"
        elif height//1 == 720:
            crop = "40,550,1200,160"
        else:
            crop = "40,550,1200,160"

    f= open(file+".avs","w", encoding = "utf8")

    f.write( """# Author       : luudanmatcuoi
# Run with AviSynth+ and InpaintDelogo plugin, using AvsPmod to open/run files.
# InpaintDelogo plugin: https://github.com/Purfview/InpaintDelogo

# Step 1: Location area contain text using InpaintLoc. Adjust "Loc" crop parameters around subtitle (aka "Left,Top,-Right,-Bottom")
# Step 2: Adjust DynTune and DynMask4H for best result...
# DynTune: Binarization threshold [luma/brighness level]. (from 1 to 254; default: 200).
#          Lower values -> mask expands more into the darker areas of video.
#          Set highest where logo/subtitle is still visible.
#          Luma range mask can be made with string: "180 - 200".
# (Là cái lấy độ sáng của chữ, để càng cao thì lấy càng nhiều chữ nhưng dễ lẫn với đồ xung quanh)

# DynMask4H:  Binarization threshold for the subtitles halo (from 1 to 200; default: 60).
#             Set lowest where the subtitle halo masking is visible and clear. If too low then some letters can disappear.
#             Use "Show=6" to finetune it.
# (Là độ khác màu giữa viền và chữ, để thấp quá thì mất chữ, để cao quá thì ko phân biệt đc viền vs chữ... nói chung tự chỉnh )


#loaddll("D:\\Videos\\lab\\libfftw3f-3.dll")
Import("InpaintDelogo.avsi")

FFmpegSource2("{}")

#InpaintLoc(Loc="{}")

InpaintDelogo(Loc="{}", Show=4, DynMask=4, DynTune=210, DynMask4H=180)

SubsMask2Img(ImgDir="{}")

""".format( join(path, file), crop, crop , join(path, file[:file.rfind(".")]) ) )

f.close()

print("done")
system('pause')