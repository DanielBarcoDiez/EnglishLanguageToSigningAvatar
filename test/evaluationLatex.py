import textProcessorTest
import wer
import time

def processFile(filename):
    results = []

    with open(filename, 'r') as file:
        total_lines = sum(1 for line in file)
        file.seek(0)
        for idx, line in enumerate(file, 1):
            originalSentence, correctSentence = line.strip().split(' / ')

            start_time = time.time()
            processedSentence = textProcessorTest.processText(originalSentence.strip())
            elapsed_time = time.time() - start_time
            results.append((originalSentence.strip(), processedSentence, correctSentence.strip(), elapsed_time))
            print(f"Processed sentence {idx}/{total_lines} in {elapsed_time:.4f} seconds")

    return results

def calculateWerForFile(results):
    werValues       = []
    total_sentences = len(results)

    for idx, (originalSentence, processedSentence, correctSentence, elapsed_time) in enumerate(results, 1):
        werScore = wer.calculateWER(correctSentence, processedSentence)
        werValues.append((originalSentence, processedSentence, correctSentence, werScore, elapsed_time))

        print(f"Calculated WER for sentence {idx}/{total_sentences}")

    return werValues

def calculateAverageWer(werValues):
    return sum(wer for _, _, _, wer, _ in werValues) / len(werValues)

def calculateAverageTime(werValues):
    return sum(time for _, _, _, _, time in werValues) / len(werValues)

def sortAndWriteResults(werValues):
    sortedWerValues = sorted(werValues, key=lambda x: x[3])
    with open('results.txt', 'a') as resultsFile:
        resultsFile.write(r"\# & \textbf{Frase original} & \textbf{Frase en orden BSL} & \textbf{Frase procesada por ELSA} & \textbf{WER (0-1)} & \textbf{Tiempo (s)} \\")
        resultsFile.write("\n\\hline\n")
        for idx, (originalSentence, processedSentence, correctSentence, werScore, elapsed_time) in enumerate(sortedWerValues, 1):
            resultsFile.write(f"{idx} & {originalSentence} & {correctSentence} & {processedSentence} & {werScore:.4f} & {elapsed_time:.4f} \\\\")
            resultsFile.write("\n\\hline\n")

if __name__ == "__main__":
    processedResults = processFile('sentences.txt')
    werValues        = calculateWerForFile(processedResults)
    averageWer       = calculateAverageWer(werValues)
    averageTime      = calculateAverageTime(werValues)

    with open('results.txt', 'w') as resultsFile:
        resultsFile.write(f"\nAverage WER: {averageWer}\n")
        resultsFile.write(f"Average processing time: {averageTime:.4f} seconds\n")

    sortAndWriteResults(werValues)
