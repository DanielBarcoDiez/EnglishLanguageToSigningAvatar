import jiwer

def calculateWER(correct, proposed):
    transforms = jiwer.Compose(
        [
            jiwer.ExpandCommonEnglishContractions(),
            jiwer.RemoveEmptyStrings(),
            jiwer.ToLowerCase(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.RemovePunctuation(),
            jiwer.ReduceToListOfListOfWords(),
        ]
    )

    wer = jiwer.wer(
                    correct,
                    proposed,
                    truth_transform=transforms,
                    hypothesis_transform=transforms,
                )
    return wer
