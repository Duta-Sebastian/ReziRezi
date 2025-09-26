import json 
from pathlib import Path 
from collections import OrderedDict
if __name__ == "__main__":
    file_jsons = "extracted_transcripts"
    names = []
    for file_json in Path(file_jsons).iterdir():
        with open(file_json, mode = 'r') as file:
            name_list = json.load(file)
            names.extend(name_list)
    counter = {}
    for name in names:
        name = name.split(' /')[0]
        name = name.split(' (')[0]
        counter[name] = counter.get(name,0) + 1
    counter = [(key,value) for key,value in counter.items()]
    counter = sorted(counter, key = lambda x: -x[1])
    with open("resume.txt", mode = 'w') as file:
        for key,value in counter:
            file.write(f"{key} : {value} \n")