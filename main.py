import os
import json
import requests
from bin_modify_utils import Ryujinx

yes = ['yes', 'ye', 'y']
convert = Ryujinx()
path = os.getenv('APPDATA')
directory = rf"{path}/Ryujinx/system/amiibo"
realpath = os.getcwd()
try:
    with open(os.path.join(directory, 'Amiibo.json')) as amiibodict:
        amiibo = json.load(amiibodict)
        amiibo = amiibo['amiibo']
except:
    amiibo = requests.get('https://amiiboapi.com/api/amiibo/').json()
    amiibo = amiibo['amiibo']

initial = input("Type 'ryuconvert' to convert from bin to ryujinx (current directory), type 'binconvert' to convert from ryujinx to bin (from the ryujinx amiibo directory).\n")

if initial == 'binconvert':
    for jsons in os.listdir(directory):
        if jsons.endswith('.json') and jsons != 'Amiibo.json':
            character = os.path.splitext(jsons)[0]
            for characters in amiibo:
                if characters['head'] + characters['tail'] == character:
                    character = characters['name']
            print(f"A json file was found! The amiibo's character is {character}.")
            y = input('Would you like to convert this file? (response must be "yes" or "no").\n')
            if y.lower() in yes:
                with open(os.path.join(directory, jsons)) as ryudata:
                    bin, chara_id = convert.json_to_bin(ryudata.read())
                    with open(os.path.join(realpath, chara_id + '.bin'), 'wb') as fp:
                        fp.write(bin)


if initial == 'ryuconvert':
    for bins in os.listdir(realpath):
        if bins.endswith('.bin'):
            print(f"A bin file was found! The filename is {bins}.")
            y = input('Would you like to convert this file? (response must be "yes" or "no").\n')
            if y == "yes":
                with open(bins, 'rb') as bin:
                    json_, chara_id = convert.bin_to_json(bin.read())
                    with open(os.path.join(realpath, chara_id.upper() + '.json'), 'w+') as charajson:
                        charajson.write(json_)
