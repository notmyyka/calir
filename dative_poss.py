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

def poss_parser_dev(sentence):
    global COUNT_NOAH
    chain = ['', '', '', '']
    progress = 0
    found = 0
    cut = other.union(ADP).union(V).union(KO).union(ADV)
    plus = {''}
    for i in cut:
        plus.add(i+'+')
    cut = cut.union(plus)
    for word in sentence:
        if word.get(POS) == 'ART' and word.text not in {'d’', 'das'}:
            progress = 1
            chain[0] = word.text
        if word.get(POS) in {'PDAT', 'PIAT'}:
            progress = 1
            chain[0] = word.text
        # substituting pronouns can replace ART NP
        if word.get(POS) in {'PDS', 'PIS', 'PWS'}:
            progress = 2
            chain[0] = ''
            chain[1] = word.text
        elif word.get(POS) in {'NN', 'NE'}:
            if progress == 1:
                progress = 2
                chain[1] = word.text
            if progress == 2:
                pass
            if progress == 3:
                progress = 0
                chain[3] = word.text
                found += 1
                COUNT_NOAH += 1
                print(chain[0], chain[1], chain[2], chain[3])
                for x in chain: x = ''
        elif word.get(POS) == 'PPOSAT':
            if progress == 2:
                if 'm' in chain[0] or 'r' in word.text:
                    progress = 3
                    chain[2] = word.text

        elif word.get(POS) in {'ADJA'}:
            pass

        elif word.get(POS) in cut:
            progress = 0
        else:
            pass
        # print(word.text, progress)
    if found:
        print(' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w']), '\n')


def poss_parser(sentence):
    chain = ['', '', '', '']
    progress = 0
    cut = other.union(ADP).union(V).union(KO).union(ADV)
    plus = {''}
    for i in cut:
        plus.add(i+'+')
    cut = cut.union(plus)
    for word in sentence:
        if word.get(POS) == 'ART' and word.text not in {'d’', 'das'}:
            progress = 1
            chain[0] = word.text
        if word.get(POS) in {'PDAT', 'PIAT'}:
            progress = 1
            chain[0] = word.text
        # substituting pronouns can replace ART NP
        if word.get(POS) in {'PDS', 'PIS', 'PWS'}:
            progress = 2
            chain[0] = ''
            chain[1] = word.text
        elif word.get(POS) in {'NN', 'NE'}:
            if progress == 1:
                progress = 2
                chain[1] = word.text
            if progress == 2:
                pass
            if progress == 3:
                progress = 0
                chain[3] = word.text
                return True
        elif word.get(POS) == 'PPOSAT':
            if progress == 2:
                if 'm' in chain[0] or 'r' in word.text:
                    progress = 3
                    chain[2] = word.text

        elif word.get(POS) in {'ADJA'}:
            pass

        elif word.get(POS) in cut:
            progress = 0
        else:
            pass
        # print(word.text, progress)
    return False


def noah_parser(infile):
    global COUNT_NOAH
    global POS
    POS = 'pos'
    print('checking ', infile, '...')
    tree = ET.parse(infile)
    document = tree.getroot()

    for article in document:
        for sentence in article:
            poss_parser_dev(sentence)


if True:
    noah_dir = os.listdir(f'{os.getcwd()}\\NOAH')
    for file in noah_dir:
        if file.endswith('.xml'):
            noah_parser(f'NOAH\\{file}')
    print(f'found {COUNT_ARCH} candidates in the ArchiMob-Corpus, {COUNT_NOAH} candidates in the NOAH-Corpus.')
    # noah_parser('NOAH\\NOAH_blogs.xml', outfile)
