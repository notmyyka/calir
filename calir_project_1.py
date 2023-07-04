import argparse
import os
# import xml
import xml.etree.ElementTree as ET
import pathlib

VERB_TAGS1 = {''}
COUNT_NOAH = 0
COUNT_ARCH = 0
# archimob tags:
#   W 
#       verbs   = VMFIN, VVFIN, VAFIN, VVPP, VAPP, VVINF, VMPP, VMINF, VAINF ...
#       NPs     = NN, PPER, ART NN, ART ADJA NN, CARD ADJA NN,  _

# PATTERN: 
def flushfile(file):
    with open(file, 'w', encoding='utf-8') as f:
        f.write('')

def archimob_parser(infile, outfile='outf.txt'):
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    root =tree.getroot()
    # with open(infile, 'r', encoding='utf-8') as file:
    #     line1 = file.readline()
    #     data = line1 + '<doc>\n' + file.read() + '\n</doc>'
    # root = ET.fromstring(data)
    
    body = root[1][0]
    # print(root.tag)
    # print(body[0][0].text)
    with open(outfile, 'a', encoding='utf-8') as outf:
        for linenr,utterance in enumerate(body,1):
            found_one = False
            for word in utterance:
                # print(word.tag[-1])
                # if (found_one is False) and word.get('tag') == 'VVFIN':
                # verb1
                if (found_one is False) and (word.get('tag') == 'VVFIN' or word.get('tag') == 'VVPP'):
                    found_one = True
                    # print(_,word.get('tag'))
                    continue
                # verb2
                elif (word.get('tag') == 'VVINF') and (found_one):
                    # print(_,word.get('tag'))
                    outf.write(f"{infile},{linenr},{' '.join([wrd.text for wrd in utterance if wrd.tag[-1] == 'w'])}\n")
                    # outf.write()
                    # COUNT_ARCH += 1
                    break
                else:
                    found_one = False
                    continue

def noah_parser(infile, outfile):
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    document =tree.getroot()
    
    with open(outfile, 'a', encoding='utf-8') as outf:
        for i,article in enumerate(document,1):
            found_one = False
            for j,sentence in enumerate(article,1):
                for word in sentence:
                    if (found_one is False) and (word.get('pos') == 'VVFIN' or word.get('pos') == 'VVPP'):
                        found_one = True
                        # print(_,word.get('tag'))
                        continue
                    elif  word.get('pos') == 'VVINF' and (found_one):
                        outf.write(f"{infile},{i},{j},{' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w'])}\n")
                        # COUNT_NOAHs += 1
                        break
                    else:
                        found_one = False
                        continue


if __name__ =='__main__':
    outfile = 'outf-archimob.txt'
    flushfile(outfile)
    with open(outfile, 'a', encoding='utf-8') as outf:
        outf.write('file,sentence nr, sentence\n')
    archimob_dir = os.listdir(f'{os.getcwd()}\\archimob')
    for file in archimob_dir:
        if file.endswith('.xml'):
            archimob_parser(f'archimob\\{file}', 'outf-archimob.txt')



    outfile = 'outf-noah.txt'
    flushfile(outfile)
    with open(outfile, 'a', encoding='utf-8') as outf:
        outf.write('file,article nr,sentence nr, sentence\n')
    noah_dir = os.listdir(f'{os.getcwd()}\\NOAH')
    for file in noah_dir:
        if file.endswith('.xml'):
            noah_parser(f'NOAH\\{file}', 'outf-NOAH.txt')
    # print(f'found {count_archimob} candiates in the ArchiMob-Corpus, {count_noah} candidates in the NOAH-Corpus.')
    # noah_parser('NOAH\\NOAH_blogs.xml', outfile)

