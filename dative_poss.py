import argparse
import os
# import xml
import xml.etree.ElementTree as ET
import pathlib

COUNT_NOAH = 0
COUNT_ARCH = 0

VV = {'VVFIN', 'VVIMP', 'VVINF', 'VVIZU', 'VVPP'}
VA = {'VAFIN', 'VAIMP', 'VAINF', 'VAPP'}
VM = {'VMFIN', 'VMINF', 'VMPP'}
V = VV.union(VA.union(VM))

ADP = {'APPR', 'APPRART', 'APPO', 'APZR'}

KO = {'KOUI', 'KOUS', 'KON', 'KOKOM'}

ADV = {'ADJD', 'ADB'}

other = {'$(', '$,'}

def ART_parser(infile, ressource='NOAH'):
    if ressource == 'NOAH':
        POS = 'pos'
        global COUNT_NOAH
        count = COUNT_NOAH
    elif ressource == 'ARCH':
        POS = 'tag'
        global COUNT_ARCH
        count = COUNT_ARCH

    tree = ET.parse(infile)
    document = tree.getroot()
    global variations
    for article in document:
        for sentence in article:
            for word in sentence:
                if word.get(POS) == 'ART':
                    variations.add(word.text.casefold())


def poss_parser(sentence, ressource='NOAH'):
    if ressource == 'NOAH':
        POS = 'pos'
        global COUNT_NOAH
        count = COUNT_NOAH
    elif ressource == 'ARCH':
        POS = 'tag'
        global COUNT_ARCH
        count = COUNT_ARCH
    filtered = ['', '', '', '']
    chain = 0
    found = 0
    global V
    cut = other.union(ADP).union(V).union(KO).union(ADV)
    plus = {''}
    for i in cut:
        plus.add(i+'+')
    cut = cut.union(plus)
    for word in sentence:
        if word.get(POS) == 'ART' and word.text not in {'d’', 'das'}:
            chain = 1
            filtered[0] = word.text
        elif word.get(POS) in {'NN', 'NE'}:
            if chain == 1:
                chain = 2
                filtered[1] = word.text
            if chain == 2:
                pass
            if chain == 3:
                chain = 0
                filtered[3] = word.text
                found += 1
                count += 1
                print(filtered[0], filtered[1], filtered[2], filtered[3])
                for x in filtered: x = ''
        elif word.get(POS) == 'PPOSAT':
            if chain == 2:
                if 'm' in filtered[0] or 'r' in word.text:
                    chain = 3
                    filtered[2] = word.text

        elif word.get(POS) in {'ADJA'}:
            pass

        elif word.get(POS) in cut:
            chain = 0
        else:
            pass
        # print(word.text, chain)
    if found:
        print(' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w']), '\n')
    COUNT_NOAH = count


def noah_parser(infile):
    global COUNT_NOAH
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    document = tree.getroot()

    for article in document:
        for sentence in article:
            poss_parser(sentence)


if True:
    noah_dir = os.listdir(f'{os.getcwd()}\\NOAH')
    variations = {""}
    for file in noah_dir:
        if file.endswith('.xml'):
            #ART_parser(f'NOAH\\{file}')
            noah_parser(f'NOAH\\{file}')
    print(variations)
    print(f'found {COUNT_ARCH} candidates in the ArchiMob-Corpus, {COUNT_NOAH} candidates in the NOAH-Corpus.')
    # noah_parser('NOAH\\NOAH_blogs.xml', outfile)
