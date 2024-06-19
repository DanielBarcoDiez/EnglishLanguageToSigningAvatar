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
    idx = 0

    for gloss, hamNosSys in wordsInSigmlCodeList:
        itemGloss = elementTree.SubElement(sigmlAsXML, 'hns_sign')
        itemGloss.set('gloss', gloss)

        phonetic = pronouncing.phones_for_word(gloss)

        itemNonManual = elementTree.SubElement(itemGloss, 'hamnosys_nonmanual')

        if phonetic and gloss not in ['?', 'NOT']:
            phoneticParsed = ''.join(filter(str.isalpha, phonetic[0])).lower()
            mouth_picture_attr = {'picture': phoneticParsed}
            elementTree.SubElement(itemNonManual, 'hnm_mouthpicture', mouth_picture_attr)

        if isAQuestion(wordsInSigmlCodeList, idx):
            elementTree.SubElement(itemNonManual, 'hnm_eyebrows', {'tag': 'FU'})

        if isAnExclamation(wordsInSigmlCodeList, idx):
            elementTree.SubElement(itemNonManual, 'hnm_eyebrows', {'tag': 'RB'})

        if isNegative(wordsInSigmlCodeList, idx):
            elementTree.SubElement(itemNonManual, 'hnm_head', {'tag': 'SH'})

        if isTheQuestionWord(wordsInSigmlCodeList, idx):
            elementTree.SubElement(itemNonManual, 'hnm_shoulder', {'tag': 'SB'})

        if gloss == 'YES':
            elementTree.SubElement(itemNonManual, 'hnm_head', {'tag': 'NO'})
        elif gloss == 'NO':
            elementTree.SubElement(itemNonManual, 'hnm_head', {'tag': 'SH'})

        if gloss not in ['?', 'NOT']:
            itemManual = elementTree.SubElement(itemGloss, 'hamnosys_manual')

            for sigmlCode in hamNosSys:
                elementTree.SubElement(itemManual, sigmlCode)

        idx += 1

    dataStr = elementTree.tostring(sigmlAsXML, encoding='unicode')

    dom = xml.dom.minidom.parseString(dataStr)

    sigmlCode = dom.toprettyxml(encoding='UTF-8').decode('utf-8')

    return sigmlCode

def isAQuestion(pairs, startIndex):
    for i in range(startIndex, len(pairs)):
        if pairs[i][0] in ['!','.',',']:
            return False
        if pairs[i][0] == '?':
            return True
    return False

def isAnExclamation(pairs, startIndex):
    for i in range(startIndex, len(pairs)):
        if pairs[i][0] in ['?','.',',']:
            return False
        if pairs[i][0] == '!':
            return True
    return False

def isNegative(pairs, startIndex):
    if (startIndex + 1 == len(pairs)):
        return False
       
def isTheQuestionWord(pairs, startIndex):
    if (startIndex + 1 == len(pairs)):
        return False

    return pairs[startIndex + 1][0] == '?'