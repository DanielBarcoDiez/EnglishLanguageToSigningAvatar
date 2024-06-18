from flask import Flask, render_template, request, jsonify, redirect
from flask_cors import CORS

import speech_recognition as sr

from back.textTo.textToHamNoSys  import textToHamNosys, FILE_PATH_NAME
from back.textTo.hamnosysToSigml import hamnosysToSigml
from back.textTo.textProcessor   import processText

app = Flask(__name__)
app.title = "ELSA"
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/translateText', methods=["GET", "POST"])
def translateText():
    if request.method == "POST":
        if request.form.get("id") == "transcribe":
            recognizer = sr.Recognizer()
            transcript = ""
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)

                    audio      = recognizer.listen(source)
                    transcript = recognizer.recognize_google(audio).lower()
            except sr.RequestError as e:
                transcript = "Could not request results; {0}".format(e)
            except sr.UnknownValueError:
                transcript = "Could not transcript audio"

            return jsonify({"transcript": transcript[:50]})
        
        elif request.form.get("id") == "translate":
            textToTranslate = request.form["textToTranslate"]
            isBSL           = request.form.get("isBSL").lower() == "true"

            processedText, processedTextWithType = processText(textToTranslate, isBSL)

            processedText = transformWordsNotInDataBase(processedText, processedTextWithType)

            hamNoSysSymbols, hamNoSysWords = textToHamNosys(processedTextWithType)

            textInSigml = hamnosysToSigml(hamNoSysSymbols, hamNoSysWords)

            return jsonify({"textInSigml": textInSigml, "translatedText": processedText.replace("_", " ")})
        
        elif request.form.get("id") == "correction":
            try:
                inputSentence      = request.form.get("inputSentence")
                translatedSentence = request.form.get("translatedSentence")
                correctSentence    = request.form.get("correctSentence")

                with open("back/DataBase/fixedSentences.txt", "a", encoding="utf-8") as file:
                    file.write(f"Input sentence:      {inputSentence}\n")
                    file.write(f"Translated sentence: {translatedSentence}\n")
                    file.write(f"Corrected sentence:  {correctSentence}\n\n")

            except Exception as e:
                pass

    return render_template('translateText.html')
def transformWordsNotInDataBase(sentence, sentenceWithType):
    transformedSentence = []

    wordInDataBase = False

    for word, wordWithType in zip(sentence.split(), sentenceWithType.split()):
        with open(FILE_PATH_NAME, "r", encoding="utf-8") as file:
            for line in file:
                columns = line.strip().split(":")
                for synonym in columns[0].split("/"):
                    if wordWithType.lower() == synonym.lower():
                        transformedSentence.append(word)
                        wordInDataBase = True
                        break

                if wordInDataBase:
                    break

            if not wordInDataBase:
                transformedWord = "-".join([letter.upper() for letter in word])
                transformedSentence.append(transformedWord)

        wordInDataBase = False

    return " ".join(transformedSentence)

if __name__ == "__main__":
    app.run(debug=True)