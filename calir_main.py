import argparse
import os
# import xml
import re,click
import xml.etree.ElementTree as ET
import pathlib

VERB_TAGS1 = {''}
COUNT_NOAH = 0


# COUNT_ARCH = 0

# archimob tags:
#   W 
#       verbs   = VMFIN, VVFIN, VAFIN, VVPP, VAPP, VVINF, VMPP, VMINF, VAINF ...
#       NPs     = NN, PPER, ART NN, ART ADJA NN, CARD ADJA NN,  _

# CODE STRUCTURE:
    # 
    #   main(LIST of input_files, output file)
    #   | clear_txtfile(output)
    #   | for each INPUT_FILE in the input_file_LIST:
    #   |   parse(input_file)
    #       | for each ARTICLE[=ET.Element] in the input_file:
    #       |   sentences = {}
    #       |   for each SENTENCE[=ET.Element] in the article:
    #       |       find_phenomenon1(sentence) 
    #       |      <-- False/True
    #       |       find_phenomenon2(sentence) -> False/True
    #       |      <-- False/True
    #       |       find_phenomenon3(sentence) -> False/True
    #       |      <-- False/True
    #       |  saved_sentences = dict{
    #                               article_n[=int] : 
    #                            {sentence (ET.Element) : 
    #                      LIST['phenomenonX', 'phenomenonY']} }
    #   |  <-- (file_name, saved_sentences)
    #   |  
    #   |  all_sentences = { file_name (str) :
    #                        saved_sentences (dict) }
    #   | second_pass(all_sentences[dict])
    #       | for FILE[str],articles[dict] in all_sentences[dict].items()
    #       |   for ARTICLE[int],(article_attributes[dict],saved_sentences[dict]) in articles[dict].items():
    #       |     for sentence[ET.Element],phenomena[list] in saved_sentences[dict].items():
    #       |       for phenomenon[str] in phenomena[list]:
    #       |         does 'sentence' really contain 'phenomenon'?
    #       |        <-- True/False
    #       |       if True:
    #       |         add phenomenon[str] to updated_phenomena[list]
    #       |     replace phenomena[list] with updated_phenomena[list]
    #   | for file_name[str],saved_sentences[dict] in all_sentences.items():
    #   |   for sentence[ET.Element], phenomena[list] in saved_sentences.items():
    #   |     write sentence to outfile, with additional tags for FILE_NAME, PHENOMENA


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
    """checks whether a sentence, in which an infinitive-particle (PTKINF) was found, also contains a full- or participle-form of the same verb."""
    # assumes that only one candidate for each sentence.
    state = (False, None)
    # store custom pattern matching functions for each type of particle (the 'K' explicitly for the Grisons dialect)
    forms={
        'g': lambda x: re.search(r'''[Gg](?:[ao](?:nge?|hne?|h|h?t)|(?:ei|ienged?|öng|önd|iech[ie]?d?|äng[ei]d?|[öä]chi|öi?))''', x),
        'c': lambda x: re.search(r'''[Cc]h(?:[uo]nn?(?:t|sch|d)|ume?|ömen?[dt]?|ond|ieme?|ämi?|oh?)''', x),
        'k': lambda x: re.search(r'''[Kk]h?(?:unn?(?:t|sch)|ume?|ömen?d?|oh)''', x),
        'a': lambda x: re.search(r'''[Ff](?:ang|[oa]h?(?:sch|(?:en?)?[td]))''', x),
        'l': lambda x: re.search(r'''[Ll](?:önd|öched(?:aa?|oo?)h?(?:sch|t|d|n))''', x)
    }
    for i, word in enumerate(sentence):
        if word.get('pos') == 'PTKINF':
            # print(word)
            if word.text.lower() in ['go', 'ga', 'goge']:
                state = ('g',i)
            elif word.text.lower() == 'cho':
                state = ('c', i)
            # just for the grisons, since the later pattern matching is based on the first latter
            elif word.text.lower() in  ['khoh','kho']:
                state = ('k',i)
            elif word.text.lower() in ['fa', 'fah', 'fo', 'foh', 'afa', 'aafa', 'aafo', 'afo', 'afoo', 'afoh', 'afah', 'aafoh', 'aafah']:
                state = ('a',i)
            elif word.text.lower() in ['lo', 'loh', 'loo', 'la', 'lah', 'laa']:
                state = ('l', i)
    # return False if we have no Infinitive-Particle at all("PTKINF")
    if state[0] is False:
        return False
    else:
        for i,word in enumerate(sentence):
            # skip the previously found token (PTKINF)
            if i == state[0]:
                continue

            # - the word occurs BEFORE the infinite particle, starts with the same letter and is a a finite verb
            if (i < state[1] and word.text.startswith(state[0]) and word.get('pos')=='VVFIN'):
                # if state[0]=='g' and word.text.startswith('g'):
                if forms[state[0]](word.text) != None:
                    print(forms[state[0]](word.text).group(0))
                    return True
            # or
            # - the word occurs AFTER the infinite particle, starts with the same letter and is a a PARTICIPLE
            elif (i < state[1] and word.text.startswith(state[0]) and word.get('pos')=='VVPP'):
                if forms[state[0]](word.text) != None:
                    print(forms[state[0]](word.text).group(0))
                    return True
            # or
            # - a very variable combination of 'cho' and 'go'
            elif ((state[0] in ['k', 'c']) and word.text.startswith('g') and (word.get('pos') in ['VVFIN','PTKINF','VVPP'])):
                if forms['g'](word.text) != None:
                    print(forms['g'](word.text).group(0))
                    return True
            # - a very variable combination of 'g' and 'cho'
            elif ((state[0]=='g') and (word.text[0] in ['k','c']) and (word.get('pos') in ['VVFIN','PTKINF','VVPP'])):
                if forms['k'](word.text) != None:
                    print(forms['k'](word.text).group(0))
                    return True
    return False


def find_csd(sentence: ET.Element) -> bool:
    # initial state: we haven't found a full-verb yet
    found_one = False
    for word in sentence:
        if (found_one is False) and (re.search("^VV", word.get('pos')) is not None):
            found_one = True
            # print(_,word.get('tag'))
            continue
        # For a crossed dependency to occur, we need the dependent verb to follow its head
        elif word.get('pos') == 'VVINF' and (found_one):
            # outf.write(f"{infile},{i},{j},{' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w'])}\n")
            # COUNT_NOAHs += 1
            return True
        else:
            found_one = False
            continue
    return False


def find_dat_possessive(sentence: ET.Element) -> bool:
    POS = 'pos'

    # as we find more and more parts of the pattern ART.DAT Noun POSS Noun, we raise our 'progress bar':
    # progress = 0 means we have no continuous candidate to match our pattern
    # progress = 1 means we've found an article that could be dative
    # progress = 2 means we have an article followed by a noun (may be intercepted by adjectives)
    # progress = 3 means we've found the first three elements: we have a match if we now find the fourth element
    progress = 0
    chain = ['', '', '', '']
    for word in sentence:

        # every dative article restarts a potential match this matching function includes a few potential mNOM articles
        if word.get(POS) == 'ART' and re.search("(m$|[eia]m)|(de$|er|dr$)", word.text) is not None:
            progress = 1
            chain[0] = word.text
        # attributing pronouns can stand in for the article
        if word.get(POS) in {'PDAT', 'PIAT'}:
            progress = 1
            chain[0] = word.text
        # substituting pronouns can replace ART NP
        if word.get(POS) in {'PDS', 'PIS', 'PWS'}:
            progress = 2
            chain[0] = ''
            chain[1] = word.text
        elif word.get(POS) in {'NN', 'NE'}:
            # If we have a preceding article, it means we have progressed further
            if progress == 1:
                progress = 2
                chain[1] = word.text
            # multi-part names (and compounds) can be smushed together.
            if progress == 2:
                pass
            # once we have the first three elements, a noun right after means we've succeeded
            if progress == 3:
                progress = 0
                chain[3] = word.text
                # our chain variable can be used to print out the found pattern for ease of correction:
                # print(' '.join([x for x in chain]))
                return True
        elif word.get(POS) == 'PPOSAT':
            if progress == 2:
                # This condition checks if the gender of the article and the possessive pronoun match up:
                # The first part considers masc/neut and the second considers fem/plur
                if (re.search("(m$|[eia]m)", chain[0]) != None and re.search("^s[iy]", word.text) is not None)\
                        or (re.search("(de$|er|dr$)", chain[0]) is not None and re.search("^[ie]h?r", word.text) is not None):
                    progress = 3
                    chain[2] = word.text
                else:
                    progress = 0
                    chain = ['', '', '', '']
        # substitutive possessives can replace POSS Noun in our pattern
        elif word.get(POS) == 'PPOSS':
            if progress == 2:
                # They still have to agree in gender with the article
                if (re.search("(m$|[eia]m)", chain[0]) != None and re.search("^s[iy]", word.text) is not None) \
                        or (re.search("(de$|er|dr$)", chain[0]) is not None and re.search("^[ie]h?r", word.text) is not None):
                    progress = 0
                    chain[2] = word.text
                    # print(' '.join([x for x in chain]))
                else:
                    progress = 0
                    chain = ['', '', '', '']
        # adjectives can go in the following positions: ART (ADJ) Noun POSS (ADJ) Noun
        elif word.get(POS) in {'ADJA'}:
            pass
        # punctuation, verbs, adpositions and adverbs quite certainly break our pattern
        elif re.search("\$|^V|^AP|^KO|ADJD|ADV", word.get(POS)) is not None:
            progress = 0
            chain = ['', '', '', '']
    return False




def parse(infile:str) -> tuple[str, dict[int,tuple[dict,dict[ET.Element,list]]]]:
    """primarily built for xml files in the format of the NOAH-corpus"""
    print('parsing ', infile, '...')
    tree = ET.parse(infile)
    document = tree.getroot()
    # hierarchy of the xml document:
    #   document > article > sentence (s) > word (w)
    filename = infile[infile.find('/')+1:-4]
    all_articles = {}
    # iterate through all articles of the document
    for i,article in enumerate(document,0):
        # save the i-th article attributes 
        # iterate through all sentences in the article
        all_sentences ={}
        for j,sentence in enumerate(article,0):
            # check for each feature whether it is contained or not
            results = {'datposs': find_dat_possessive(sentence),
                       'csd': find_csd(sentence),
                       'reduplication': find_reduplication(sentence)}
            # only save current sentence if it has one (or multiple) of the features we want to extract:
            if contains_true(results.values()):
                all_sentences[sentence] = [key for key,value in results.items() if value]
        # in the articles-dictionary (where each item is an article), save a tuple containing 
        # - the attributes of the article (we don't want/need the entire article saved)
        # - the dictionary of sentences { <Element 's' at 0x... : [phenomenon_x, ...] }
        all_articles[i] = (article.attrib, all_sentences)
    return filename, all_articles


def check_sentence_2ndpass(sentence: ET.Element, phenomena_list: list[str]) -> list:
    mapping = {'datposs':'Dative + Possessive Pronoun Constructions', 
                'csd': 'Cross-Serial Dependencies', 
                'reduplication': 'Verb Reduplication'}
    # list of which phenomena to go over in the second-pass
    check_for_these = ['csd']
    # create a copy of the list containing the supposed phenomena of each sentence
    updated_phenomena_list = phenomena_list.copy()

    # go through all phenomena that need a manual check... (i.e. only cross-serial dependencies, currently)
    for phenomenon in check_for_these:
        # skip if the phenomenon is not assumed to be present in the current sentence anyways
        if phenomenon not in phenomena_list:
            continue
        # remove the entry for e.g. 'csd' from the updated list
        updated_phenomena_list.remove(phenomenon)
        prompt=f'Does the following sentence contain any {mapping[phenomenon]}? \n\n\"{" ".join([wrd.text for wrd in sentence if wrd.tag[-1] == "w"])}\"\nAnswer: [y/n]'
        response = input(prompt)
        # if the answer is yes: re-add the phenomenon to the updated list 
        if response.lower() == 'y': 
            updated_phenomena_list.append(phenomenon)
        # if the answer is no: don't add it (do nothing) 
        if response.lower() == 'n':
            continue
    # return the updated list WITHOUT the phenomenon in it
    return updated_phenomena_list
    


def second_pass(all_files: dict[str , dict[int,tuple[dict,dict[ET.Element,list]]]]) -> dict[str , dict[int,tuple[dict,dict[ET.Element,list]]]]:
    """go over the preliminary output-file and review all the cases of an assumed cross-serial dependency (CSD) in an interactive CLI.
    Necessary because the current way of finding CSDs is high recall but very low precision, and thus needs manual checking."""
    
    # initialize the new all-sentences dictionary to which the updated items will be added
    passed_allfiles = {} 
    # iterate through the top-level dictionary (all_sentences)...
    for filename, articles in all_files.items():
        passed_articles = {}
        for index,(art_attrib,sentences) in articles.items():
            # initialize the new file-sentences dictionary to which the updated items will be added
            passed_sentences = {}
            # iterate through the lower-level dictionary (containing all relevant sentences from a specific file)
            for sentence, phenomena_list in sentences.items():
                # retrieve the list with the wrongly found phenomena removed
                updated_phenomena_list = check_sentence_2ndpass(sentence, phenomena_list)
                passed_sentences[sentence] = updated_phenomena_list
            passed_articles[index] = (art_attrib, passed_sentences)
        passed_allfiles[filename] = passed_articles
    return passed_allfiles

        
def main(infiles: list[str], outfile: str):
    """Takes a list of input files (.xml files from the NOAH corpus) and an output file.
    Writes all sentences that contain at least one of the phenomena we are looking for to the output file."""
    
    # empty the output file, just in case
    clear_txtfile(outfile)

    mapping = {'datposs':'Dative + Possessive Pronoun Constructions', 
                'csd': 'Cross-Serial Dependencies', 
                'reduplication': 'Verb Reduplication'}
    
    all_files = {}
    for file in infiles:
        filename, saved_articles = parse(file)
        all_files[filename] = saved_articles
    all_files = second_pass(all_files)
    document = ET.Element('document', attrib={'dialect': 'various', 'title':'?'})
    for idx_file, (filename, articles) in enumerate(all_files.items()):
        m_file = f'{idx_file}'
        file = ET.SubElement(document, 'file', attrib={'n': str(idx_file), 'title': filename})
        for idx_art, (article_attributes, sentences) in articles.items():
            if sentences == {}: continue
            article = ET.SubElement(file, 'article', attrib=article_attributes)
            for sentence,phenomena in sentences.items():
                for phen in phenomena: 
                    sentence.attrib[phen] = 'yes'
                article.append(sentence)
    tree = ET.ElementTree(document)
    ET.indent(tree, space="  ", level=1)
    tree.write(outfile,encoding='utf-8', xml_declaration=True, short_empty_elements=False)



def test_individual_functions(infile):
    tree = ET.parse(infile)
    document = tree.getroot()
    # iterate through all articles of the document
    for i, article in enumerate(document, 0):
        # iterate through all sentences in the article
        for j, sentence in enumerate(article, 0):
            pass
            # INSERT FUNCTION TO BE TESTED HERE:
            # if find_reduplication(sentence):
            # if find_csd(sentence):
            # if find_dat_possessive(sentence):
                # print('found_one')
                # print(' '.join([wrd.text for wrd in sentence if wrd.tag[-1] == 'w']))
    pass


if __name__ == '__main__':
    pass
    # test_individual_functions('NOAH/NOAH_blogs.xml')

    outfile = 'output-main.xml'
    inputfiles = ['NOAH/NOAH_blogs.xml','NOAH/NOAH_blick.xml','NOAH/NOAH_schobinger.xml','NOAH/NOAH_wiki.xml','NOAH/NOAH_swatch.xml']
    # inputfiles = ['NOAH/NOAH_blogs.xml']
    main(inputfiles, outfile)

    
    # clear_txtfile(outfile)
    # with open(outfile, 'a', encoding='utf-8') as outf:
    #     outf.write('file,article nr,sentence nr, sentence\n')
    # noah_dir = os.listdir(f'{os.getcwd()}/NOAH')
    # for file in noah_dir:
    #     if file.endswith('.xml'):
    #         parse(f'NOAH/{file}', 'outf-NOAH.txt')
