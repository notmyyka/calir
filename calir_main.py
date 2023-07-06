import argparse
import os
# import xml
import re
import xml.etree.ElementTree as ET
import pathlib

VERB_TAGS1 = {''}
COUNT_NOAH = 0
# COUNT_ARCH = 0

# archimob tags:
#   W 
#       verbs   = VMFIN, VVFIN, VAFIN, VVPP, VAPP, VVINF, VMPP, VMINF, VAINF ...
#       NPs     = NN, PPER, ART NN, ART ADJA NN, CARD ADJA NN,  _



def clear_txtfile(file):
    """empty a file from all existing content."""
    with open(file, 'w', encoding='utf-8') as f:
        f.write('')


def contains_true(ls: list[bool]):
    """returns True if one element of the list is True"""
    for boolean in ls:
        if boolean:
            return True
        else:
            continue
    return False


def find_reduplication(sentence: ET.Element) -> bool:
    """checks whether a sentence contains reduplication of 'go', 'cho' or 'lah'."""
    # assumes that only one candidate for each sentence.
    state = (False, None)
    forms={
        # 'g':['gang', 'gahn', 'gohn', 'gahne', 'gange', 'gahsch', 'gasch', 'geisch', ],
        # 'g': lambda x: re.search(r'''[Gg]
        #                     (?:[ao](?:nge?|hne?|h)?
        #                         |(?:öi?|ei|ienged?|öng|önd|iech[ie]?d?|äng[ei]d?|[öä]chi|))''', x),
        'g': lambda x: re.search(r'''[Gg](?:[ao](?:nge?|hne?|h)|(?:ei|ienged?|öng|önd|iech[ie]?d?|äng[ei]d?|[öä]chi|öi?))''', x),
        'c': lambda x: re.search(r'''[Cc]h''', x),
        'k': lambda x: re.search(r'''[Kk]h?(?:unn?(?:t|sch)|um|ömen?d?)''', x),
        'a': lambda x: re.search(r'''[Aa]''', x),
        'l': lambda x: re.search(r'''[Ll]''', x),
    }
    for i,word in enumerate(sentence):
        if word.get('pos') == 'PTKINF':
            # print(word)
            if word.text.lower() == 'go':
                state = ('g',i)
            elif word.text.lower() == 'cho':
                state = ('c',i)
            # just for the grisons, since the later pattern matching is based on the first latter
            elif word.text.lower() ==  'khoh':
                state = ('k',i)
            elif word.text.lower() in ['afa', 'aafa','a', 'aafo', 'afo', 'afoo', 'afoh', 'afah', 'aafoh', 'aafah']:
                state = ('a',i)
            elif word.text.lower() in ['lo', 'loh', 'loo', 'la', 'lah', 'laa']:
                state = ('l',i)
    # return False if we have no Infinitive-Particle at all("PTKINF")
    if state[0] is False: return False
    else:
        for i,word in enumerate(sentence):
            # if 
            # - the word occurs BEFORE the infinite particle, starts with the same letter and is a a finite verb
            if (i < state[1] and word.text.startswith(state[0]) and word.get('pos')=='VVFIN'):
                if state[0]=='g' and word.text.startswith('g'):
                    if forms['g'](word.text) != None:
                        return True
            # elif (i < state[1] and word.text.startswith(state[0]) and word.get('pos')=='VVFIN'):
            #     return True
            # # or
            # # - the word occurs AFTER the infinite particle, starts with the same letter and is a a PARTICIPLE
            # elif (i < state[1] and word.text.startswith(state[0]) and word.get('pos')=='VVPP'):
            #     return True
            #     pass
            # # or
            # # - a very variable combination of 'cho' and 'go'
            # elif (i != state[1] and (state[0] in ['k', 'c']) and word.text.startswith('g') and word.get('pos') in ['VVFIN','PTKINF','VVPP']):
            #     return True
            #     pass
            # # - a very variable combination of 'g' and 'cho'
            # elif (i != state[1] and (state[0]=='g') and (word.text[0] in ['k','c']) and word.get('pos') in ['VVFIN','PTKINF','VVPP']):
            #     return True
            #     pass
    return False

def find_csd(sentence: ET.Element) -> bool:
    # initial state: we haven't found a full-verb yet
    found_one = False
    for word in sentence:
        if (found_one is False) and (word.get('pos') == 'VVFIN' or word.get('pos') == 'VVPP'):
            found_one = True
            # print(_,word.get('tag'))
            continue
        elif word.get('pos') == 'VVINF' and (found_one):
            # outf.write(f"{infile},{i},{j},{' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w'])}\n")
            # COUNT_NOAHs += 1
            return True
        else:
            found_one = False
            continue
    return False
    
def find_dat_possessive(sentence: ET.Element) -> bool:
    pass




def parse(infile:str, outfile:str) -> tuple[str,dict]:
    """primarily built for xml files in the format of the NOAH-corpus"""
    print('parsing ', infile, '...')
    tree = ET.parse(infile)
    document =tree.getroot()
    # hierarchy of the xml document:
    #   document > article > sentence (s) > word (w)
    filename = infile[infile.find('/')+1:-4]
    saved_elements = {}
    # iterate through all articles of the document
    for i,article in enumerate(document,0):
        # iterate through all sentences in the article
        for j,sentence in enumerate(article,0):
            # check for each feature whether it is contained or not
            results = {'datposs':find_dat_possessive(sentence), 
                        'csd': find_csd(sentence), 
                        'reduplication': find_reduplication(sentence)}
            # only save current sentence if it has one (or multiple) of the features we want to extract:
            if contains_true(results.values()):
                saved_elements[sentence] = [item.key() for item in results if item.value()]
                # TODO delete later, checking only
                print(saved_elements)

    return filename, saved_elements
                
                

def second_pass(infile: str, outfile: str):
    """go over the preliminary output-file and review all the cases of an assumed cross-serial dependency (CSD) in an interactive CLI.
    Necessary because the current way of finding CSDs is high recall but very low precision, and thus needs manual checking."""
    pass

def main(infiles: list[str], outfile: str):
    clear_txtfile(outfile)
    combined_outputs = {}
    for file in infiles:
        filename, resultdict = parse(file)

    with open(outfile, 'a', encoding='utf-8') as outf:
        pass

def test_individual_functions(infile):
    tree = ET.parse(infile)
    document =tree.getroot()
    # iterate through all articles of the document
    for i,article in enumerate(document,0):
        # iterate through all sentences in the article
        for j,sentence in enumerate(article,0):

# INSERT FUNCTION TO BE TESTED HERE:
            if find_reduplication(sentence):
            # if find_csd(sentence):
            # if find_dat_possessive(sentence):
                print('found_one')
                print(' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w']))
    pass    


if __name__ =='__main__':
    pass
    # aaaa= re.search(, 'gönd').group(0)
    # print(aaaa)
    test_individual_functions('NOAH/NOAH_blogs.xml')


    # outfile = 'outf-noah.txt'
    # clear_txtfile(outfile)
    # with open(outfile, 'a', encoding='utf-8') as outf:
    #     outf.write('file,article nr,sentence nr, sentence\n')
    # noah_dir = os.listdir(f'{os.getcwd()}/NOAH')
    # for file in noah_dir:
    #     if file.endswith('.xml'):
    #         parse(f'NOAH/{file}', 'outf-NOAH.txt')


