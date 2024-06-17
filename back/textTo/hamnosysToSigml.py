import os

import xml.etree.ElementTree as elementTree
import xml.dom.minidom

import pronouncing

def hamnosysToSigml(hamnosysSymbols, hamnosysWords):
    global sigmlAsXML

    sigmlAsXML = elementTree.Element('sigml')

    hamnosysSymbolsUnicodesList = []

    for char in hamnosysSymbols:
        hamnosysUnicode = char.encode('unicode_escape').decode().replace('\\u', '').upper()
        hamnosysSymbolsUnicodesList.append(hamnosysUnicode)

    wordsInSigmlCodeList = wordsToSigmlCode(hamnosysWords, hamnosysSymbolsUnicodesList)

    return writeSigml(wordsInSigmlCodeList)

def wordsToSigmlCode(wordGlosses, wordUnicodes):
    wordsInSigmlCodeList = []

    hamnosysGlossesAndUnicodes = [(wordGlosses[i], wordUnicodes[i]) for i in range(0, len(wordUnicodes))]

    for i in range(0, len(hamnosysGlossesAndUnicodes)):
        hamnosysGloss    = hamnosysGlossesAndUnicodes[i][0]
        hamnosysUnicodes = hamnosysGlossesAndUnicodes[i][1]

        hamnosysUnicodesList = createHamnosysUnicodesList(hamnosysUnicodes)

        wordsInSigmlCodeList.append(hamnosysUnicodeToSigmlCode(hamnosysGloss, hamnosysUnicodesList))

    return wordsInSigmlCodeList

def createHamnosysUnicodesList(codes):
    hamnosysList = []
    n = 4 

    for j in range(0, len(codes), n):
        singleCode = codes[j : j+n]
        hamnosysList.append(singleCode)

    return hamnosysList

def hamnosysUnicodeToSigmlCode(gloss, hamnosysCodes):
    actualDirectory = os.path.dirname(os.path.abspath(__file__))
    conversionTXT   = os.path.join(actualDirectory, '..', 'DataBase', 'conversionSpreadSheet.txt')

    sigmlList = []

    with open(conversionTXT, 'r') as f:
        for code in hamnosysCodes:
            f.seek(0)
            for line in f:
                if code in line:
                    sigmlList.append(line.split(':')[0])
                    break

    return (gloss, sigmlList)

def writeSigml(wordsInSigmlCodeList): 
    for gloss, hamNosSys in wordsInSigmlCodeList:
        if gloss == '?':
            gestGloss = elementTree.SubElement(sigmlAsXML, 'hamgestural_sign')
            gestGloss.set('gloss', '?')

            gestNonManual  = elementTree.SubElement(gestGloss    , 'sign_nonmanual')
            shouderTier    = elementTree.SubElement(gestNonManual, 'shoulder_tier')
            shouderMovement= elementTree.SubElement(shouderTier  , 'shoulder_movement ')
            shouderMovement.set('movement', 'SB')

            elementTree.SubElement(gestGloss, 'sign_manual')

        else:
            itemGloss = elementTree.SubElement(sigmlAsXML, 'hns_sign')
            itemGloss.set('gloss', gloss)

            phonetic = pronouncing.phones_for_word(gloss)
            if phonetic:
                phoneticParsed = ''.join(filter(str.isalpha, phonetic[0])).lower()

                itemNonManual      = elementTree.SubElement(itemGloss, 'hamnosys_nonmanual')
                mouth_picture_attr = {'picture': phoneticParsed}

                elementTree.SubElement(itemNonManual, 'hnm_mouthpicture', mouth_picture_attr)

            itemManual = elementTree.SubElement(itemGloss, 'hamnosys_manual')

            for sigmlCode in hamNosSys:
                elementTree.SubElement(itemManual, sigmlCode)

    dataStr = elementTree.tostring(sigmlAsXML, encoding='unicode')

    dom = xml.dom.minidom.parseString(dataStr)

    sigmlCode = dom.toprettyxml(encoding='UTF-8').decode('utf-8')

    return sigmlCode