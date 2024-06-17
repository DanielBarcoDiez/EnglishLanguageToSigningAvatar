import stanza
stanza.download("en")
nlp = stanza.Pipeline("en")

import contractions

from num2words import num2words

import re

from spello.model import SpellCorrectionModel  
sp = SpellCorrectionModel(language='en')  

expressions = [
    "do not know",
    "every day",
    "give birth",
    "grow up",
    "ice cream",
    "in front of",
    "look after",
    "no one",
    "open minded",
    "pay me",
    "seat belt",
    "step on",
    "turn off", "switch off",
    "town hall",
    "traffic light", "traffic lights",
    "turn on", "switch on",
    "watch out",
    "write down",
    "eight o clock",
    "eleven o clock",
    "five o clock",
    "four o clock",
    "half past",
    "have a look",
    "help me",
    "help you",
    "let me know",
    "nine o clock",
    "one o clock",
    "quarter past",
    "quarter to",
    "seven o clock",
    "six o clock",
    "ten o clock",
    "three o clock",
    "two o clock",
    "break in",
    "wipe off",
    "sit and meet",
    "come over",
    "Bear with it",
    "go with you",
    "poor you",
    "hold on",
    "open door", "open doors",
    "turn left",
    "twelve o clock",
    "light house",
    "sign language",
    "father in law",
    "mother in law",
    "thank you",
    "seat belt"
]

expressionsReplacement = {
    "at last": "ultimately",
    "get down": "begin",
    "boundary line": "border",
    "male child": "boy",
    "calm down": "calm",
    "hash out": "discuss",
    "every day": "daily",
    "from time to time": "occasionally",
    "one half": "half",
    "fine looking": "handsome",
    "pull off": "manage",
    "mobile phone": "phone",
    "one fourth": "qarter",
    "keep quiet": "quiet",
    "straight ahead": "directly",
    "take a bath": "bathe",
    "think about something": "entertain",
    "throw away": "discard",
    "break in": "enter",
    "united states of america": "USA",
    "look for" : "seek"
}

questionExpressions = [
    "how many",
    "how much",
    "how old",
    "how long"
]

predefinedTemporalExpressions = [
    "all day",
    "all week",
    "this month",
    "this year",
    "this day",
    "later",
    "every year",
    "each year",
    "next year",
]

def changeExpressions(sentence):
    for expression in expressions + questionExpressions + predefinedTemporalExpressions:
        sentence = sentence.replace(expression, expression.replace(" ", "_"))

    return sentence

dicWordsAndUpos = {}

def addWordUpos(sentence):
    doc = nlp(sentence)

    global dicWordsAndUpos
    dicWordsAndUpos.clear()

    for sent in doc.sentences:
        for word in sent.words:
            if "_" in word.text:
                dicWordsAndUpos[word.text] = "EXP"
            else:
                dicWordsAndUpos[word.text] = word.upos

def getTemporalExpressions(sentence):
    doc = nlp(sentence)

    temporalExpressions = []

    for sent in doc.sentences:
        for word in sent.words:
            if word.deprel and "tmod" in word.deprel:
                temporalExpressions.append({"id": word.id, "text": word.text})
                for dependency in sent.words:
                    if dependency.head == word.id:
                        temporalExpressions.append({"id": dependency.id, "text": dependency.text})

        if len(temporalExpressions) == 0:
            for word in sent.words:
                if word.upos == "VERB":
                    if "Tense=Pres" in word.feats:
                        return [""]
                    if "Tense=Past" in word.feats:
                        return ["past"]
                if (word.upos == "AUX" or word.upos == "VERB") and "Tense=Fut" in word.feats and word.lemma != "will":
                    return ["future"]

        temporalExpressionsSorted = sorted(temporalExpressions, key=lambda x: x['id'])
        temporalExpressionsText   = [word['text'] for word in temporalExpressionsSorted]

        return temporalExpressionsText

def findAdjectivesForNoun(sentence, nounId):
    doc = nlp(sentence)

    nounAndAdjectives = {}

    for sent in doc.sentences:
        for word in sent.words:
            if word.head == nounId and word.xpos in ["JJ", "JJR", "JJS", "CD", "PDT", "PRP$"]:
                if nounId not in nounAndAdjectives:
                    nounAndAdjectives[nounId] = []
                nounAndAdjectives[nounId].append(word.text)

    return nounAndAdjectives

def getNounsAndAdjectivesNumbersPosessivePronouns(sentence):
    doc = nlp(sentence)

    nounAndAdjectives = {}

    for sent in doc.sentences:
        for word in sent.words:
            if word.upos == "NOUN":
                nounAndAdjectives = nounAndAdjectives | findAdjectivesForNoun(sentence, word.id)

    return nounAndAdjectives

def getTreeWords(tree):
    words = []

    if not tree.children:
        words.append(str(tree))
    else:
        for child in tree.children:
            words.extend(getTreeWords(child))

    return words

def splitSentences(sentence):
    sentences = []

    doc = nlp(sentence)

    for sent in doc.sentences:
        countS = str(sent.constituency).count("(S ")
        if countS <= 1:
            countS += str(sent.constituency).count("(VP ")

        if countS <= 1:
            sentences.append(sent.text)
        else:
            for children in sent.constituency.children[0].children:
                originalSentence = getTreeWords(children)
                sentences.append(" ".join(originalSentence))

    return sentences

def expandContractions(sentence):
    return contractions.fix(sentence)

def numericFormConversion(sentence):
    newSentence = []

    ordinalPatron = r'\b(\d+)(st|nd|rd|th)\b'

    ordinalNumbers = re.finditer(ordinalPatron, sentence)

    for match in ordinalNumbers:
        ordinal  = str(match.group(0))
        cardinal = str(match.group(1))

        sentence = sentence.replace(ordinal, cardinal)

    for word in sentence.split():
        try:
            number = int(word)
            newSentence.append(num2words(number))
        except ValueError:
            newSentence.append(word)
            continue

    return ' '.join(newSentence)

def correctSentence(sentence):
    correctedSentence = sp.spell_correct(sentence)
    return correctedSentence

def preProcess(sentence):
    sentence = sentence.lower()

    for expression in expressionsReplacement.keys():
        if expression.lower() in sentence:
            sentence = sentence.replace(expression.lower(), expressionsReplacement[expression].lower())

    sentence = changeExpressions(sentence)

    preProcessedSentence = expandContractions(sentence)
    preProcessedSentence = numericFormConversion(preProcessedSentence)
    
    preProcessedSentence = preProcessedSentence.replace("I am", "me")

    addWordUpos(preProcessedSentence)

    return preProcessedSentence

def getTypeOfWordWithId(sentence, types):
    doc = nlp(sentence)

    typeOfWords = {}

    for sent in doc.sentences:
        for word in sent.words:
            if word.xpos in types:
                if word.id not in typeOfWords:
                    typeOfWords[word.id] = []
                typeOfWords[word.id] = word.text

    return typeOfWords

def getOtherWords(sentence):
    doc = nlp(sentence)

    interjections = []
    please = []
    determiners = []
    prepositions = []
    adjectivesNumbersPosessivePronouns = []
    pronouns = []
    foreignWords = []
    verbsAdverbs = []
    existentialModals = []
    questionWords = []
    negations = []

    for sent in doc.sentences:
        for word in sent.words:
            if word.lemma == "please" or word.lemma == "sorry":
                    please.append(word.text)
            elif word.xpos in ["UH"]:
                if word.lemma == "please" or word.lemma == "sorry":
                    continue
                else:
                    interjections.append(word.text)
            elif word.xpos in ["DT"]:
                determiners.append(word.text)
            elif word.xpos in ["IN"]:
                prepositions.append(word.text)
            elif word.xpos in ["JJ", "JJR", "JJS", "CD", "PDT", "PRP$"]:
                adjectivesNumbersPosessivePronouns.append(word.text)
            elif word.xpos in ["FW"]:
                foreignWords.append(word.text)
            elif word.xpos in ["VBD", "VBG", "VBN", "VBP", "VBZ", "VB", "RB", "RBR", "RBS", "RP"]:
                if word.text == "not":
                    negations.append(word.text)
                else:
                    verbsAdverbs.append(word.text)
            elif word.xpos in ["EX", "MD"]:
                existentialModals.append(word.text)
            elif word.xpos in ["PRP"]:
                pronouns.append(word.text)
            elif word.xpos in ["WDT", "WP", "WP$", "WRB"]:
                questionWords.append(word.text)

    return interjections, please, determiners, prepositions, adjectivesNumbersPosessivePronouns, foreignWords, verbsAdverbs, existentialModals, pronouns, questionWords, negations

def joinAdjectivesAndNouns(nouns, nounsAndAdjectivesNumbersPosessivePronouns):
    adjectivesAndNouns = ""

    for nounId in nounsAndAdjectivesNumbersPosessivePronouns:
        noun = nouns[nounId]
        if (noun):
            all = nounsAndAdjectivesNumbersPosessivePronouns[nounId]
            if all:
                possessives = []
                adjectivesNumbers = []
                for word in all:
                    if dicWordsAndUpos.get(word) == 'PRON':
                        possessives.append(word)
                    else:
                        adjectivesNumbers.append(word)

                adjectivesAndNouns += " " + " ".join(adjectivesNumbers) + " " + noun + " " + " ".join(possessives) + " "
    
    return adjectivesAndNouns.split()

def process(sentence):
    processedCompleteSentence = ""

    questionWords = []
    temporalExpressions = []

    doc = nlp(sentence)

    for sent in doc.sentences:
        processedSentence = ""

        sentences = splitSentences(sent.text)

        hasInterrogation = "?" in sent.text
        hasExclamation   = "!" in sent.text

        for sent in sentences:
            temporalExpressions.extend(getTemporalExpressions(sent))

            for tExpression in predefinedTemporalExpressions:
                if tExpression.replace(" ", "_") in sent:
                    temporalExpressions.append(tExpression.replace(" ", "_"))

            for qExpression in questionExpressions:
                if qExpression.replace(" ", "_") in sent:
                    questionWords.append(qExpression.replace(" ", "_"))

            # remove temporal expressions and question expressions from sentence to analyze
            pattern = r'\b(?:' + '|'.join(re.escape(expr) for expr in temporalExpressions + questionWords) + r')\b'
            sent = re.sub(pattern + r'[.,!?;:]?', '', sent)
            sent = re.sub(r'\s+', ' ', sent).strip()

            nouns                                      = getTypeOfWordWithId(sent, ["NN", "NNP", "NNS", "NNPS"])
            nounsAndAdjectivesNumbersPosessivePronouns = getNounsAndAdjectivesNumbersPosessivePronouns(sent)

            interjections, please, determiners, prepositions, adjectivesNumbersPosessivePronouns, foreignWords, verbsAdverbs, existentialModals, pronouns, qWords, negations = getOtherWords(sent)
            questionWords.extend(qWords)

            adjectivesAndNouns = joinAdjectivesAndNouns(nouns, nounsAndAdjectivesNumbersPosessivePronouns)

            adjectivesNumbersPosessivePronouns = [adj for adj in adjectivesNumbersPosessivePronouns if adj not in adjectivesAndNouns]
            nouns                              = [noun for noun in nouns.values() if noun not in adjectivesAndNouns]

            processedSentence += ((" ").join(interjections) + " " +
                                    (" ").join(determiners) + " " +
                                    (" ").join(prepositions) + " " +
                                    (" ").join(adjectivesNumbersPosessivePronouns) + " ES" +
                                    (" ").join(adjectivesAndNouns) + " " +
                                    (" ").join(nouns) + " " +
                                    (" ").join(foreignWords) + " " +
                                    (" ").join(existentialModals) + " " +
                                    (" ").join(verbsAdverbs) + " " +
                                    (" ").join(pronouns) + " " +
                                    (" ").join(negations) + " " +
                                    (" ").join(please) + " "
                                    )

        processedCompleteSentence += " ".join(temporalExpressions) + " " + processedSentence + " " + " ".join(questionWords)

        if hasInterrogation:
            processedCompleteSentence += "?"
        elif hasExclamation:
            processedCompleteSentence += "!"

    return processedCompleteSentence.strip()

def postProcess(sentence):
    postProcessedSentenceWithType = []
    postProcessedSentence         = []

    doc = nlp(sentence)

    for sent in doc.sentences:
        for word in sent.words:
            if word.text in ["past", "future"]:
                postProcessedSentenceWithType.append(word.text + "(NOUN)")
                postProcessedSentence.append(word.text)
                continue
            if word.text not in dicWordsAndUpos.keys():
                continue
            if dicWordsAndUpos[word.text] == 'DET' and word.text in ["a", "an", "the"]:
                continue
            if dicWordsAndUpos[word.text] == "AUX" and word.text not in ["will"]:
                continue
            if word.text in ["to", "it", "for", "of"]:
                continue
            if (word.text == "i" or word.text == "me") and dicWordsAndUpos[word.text] == "PRON":
                postProcessedSentenceWithType.append("me(PRON)")
                postProcessedSentence.append("me")
                continue

            if word.text.replace("_", " ") in expressions + questionExpressions + predefinedTemporalExpressions:
                postProcessedSentenceWithType.append(word.text + "(EXP)")
                postProcessedSentence.append(word.text)
            else:
                postProcessedSentenceWithType.append(word.lemma + "(" + dicWordsAndUpos[word.text] + ")")
                postProcessedSentence.append(word.lemma)

    postProcessedSentenceWithType = (" ").join(postProcessedSentenceWithType)
    postProcessedSentence         = (" ").join(postProcessedSentence)

    return postProcessedSentence, postProcessedSentenceWithType

def processText(sentence, isBSL):
    preProcessedSentence = preProcess(sentence)

    if isBSL:
        processedSentence = process(preProcessedSentence)
    else:
        processedSentence = preProcessedSentence

    postProcessedSentence, postProcessedSentenceWithType = postProcess(processedSentence)
    return postProcessedSentence.strip(), postProcessedSentenceWithType.strip()