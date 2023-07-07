import os
# import xml
import xml.etree.ElementTree as ET

total = 0
def count_tokens(infile):
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    document =tree.getroot()
    global total
    count = 0
    for i,article in enumerate(document,1):
        for j,sentence in enumerate(article,1):
            for word in sentence:
                count += 1
    print(count, "tokens")
    total += count

def dialect_tags(infile)

noah_dir = os.listdir(f'{os.getcwd()}\\NOAH')
for file in noah_dir:
    if file.endswith('.xml'):
        count_tokens(f'NOAH\\{file}')
print("Total", total, "tokens")