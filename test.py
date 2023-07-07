import xml.etree.ElementTree as ET


infile = 'NOAH/NOAH_blogs.xml'
tree = ET.parse(infile)
document =tree.getroot()
outdict = {}
for article in document:
    # print(article.attrib)
    artdict = {}
    for sentence in article:
        artdict[sentence] = 'a'
    outdict[article.attrib['n']] = (article.attrib, artdict)
    break
# print(outdict)

mydict = {1:(2,3), 4:(5,6)}
for one,(two,three) in mydict.items():
    print(one, two, three)

