import argparse
import os
# import xml
import xml.etree.ElementTree as ET
import pathlib

VERB_TAGS1 = {''}
VV = {'VVFIN', 'VVIMP', 'VVINF', 'VVIZU', 'VVPP'}
VA = {'VAFIN', 'VAIMP', 'VAINF', 'VAPP'}
VM = {'VMFIN', 'VMINF', 'VMPP'}
V = VV.union(VA.union(VM))

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
    global COUNT_ARCH
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
            verb_counter = 0
            concat_counter = 0
            max_concat = 0
            for word in utterance:
                # print(word.tag[-1])
                # each verb starts/continues a line of verbs
                if word.get('tag') in VV:
                    verb_counter += 1
                    concat_counter += 1
                    # print(_,word.get('tag'))
                    continue
                elif concat_counter:
                    max_concat = max(concat_counter, max_concat)
                    concat_counter = 0
            else: max_concat = max(concat_counter, max_concat)
            if max_concat >= 2:
                outf.write(f"{infile}, utterance {linenr}, #verbs {verb_counter}, longest chain {max_concat} {' '.join([wrd.text for wrd in utterance if wrd.tag[-1] == 'w'])}\n")
                COUNT_ARCH += 1

def noah_parser(infile, outfile):
    global COUNT_NOAH
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    document =tree.getroot()
    
    with open(outfile, 'a', encoding='utf-8') as outf:
        for i,article in enumerate(document,1):
            for j,sentence in enumerate(article,1):
                verb_counter = 0
                concat_counter = 0
                max_concat = 0
                for word in sentence:
                    # print(word.tag[-1])
                    # each verb starts/continues a line of verbs
                    if word.get('pos') in VV:
                        verb_counter += 1
                        concat_counter += 1
                        # print(_,word.get('pos'))
                        continue
                    elif concat_counter:
                        max_concat = max(concat_counter, max_concat)
                        concat_counter = 0
                else: max_concat = max(concat_counter, max_concat)
                if max_concat >= 2:
                    outf.write(f"{infile}, article {i}, sentence {j}, #verbs {verb_counter}, longest chain {max_concat} {' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w'])}\n")
                    COUNT_NOAH += 1


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

    print(f'found {COUNT_ARCH} candidates in the ArchiMob-Corpus, {COUNT_NOAH} candidates in the NOAH-Corpus.')
    # noah_parser('NOAH\\NOAH_blogs.xml', outfile)

