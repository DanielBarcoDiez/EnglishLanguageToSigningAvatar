import os

actualDirectory   = os.path.dirname(os.path.abspath(__file__))
databaseDirectory = os.path.join(actualDirectory, '..', 'DataBase')
FILE_PATH_NAME    = os.path.join(databaseDirectory, 'hamNoSysEN.txt')

def textToHamNosys(text):
    listSimbols = []
    listWords = []

    for word in text.split():
        if word.split("(")[0] == '?':
            listSimbols.append("?")
            listWords.append(word.upper().split("(")[0])
            
            continue

        wordSymbol = findWord(word)
        if (wordSymbol):
            listSimbols.append(wordSymbol)
            listWords.append(word.upper().split("(")[0])
        else:
            for letter in word.split("(")[0]:
                letterSymbol = findWord(letter)
                if (letterSymbol):
                    listSimbols.append(letterSymbol)
                    listWords.append(letter.upper())

    return listSimbols, listWords

def findWord(word: str):
    with open(FILE_PATH_NAME, 'r', encoding='utf-8') as file:
        for line in file:
            columns = line.strip().split(':')
            synonyms = columns[0]
            for synonym in synonyms.split("/"):
                if word.lower() == synonym.lower():
                    return columns[1]
    