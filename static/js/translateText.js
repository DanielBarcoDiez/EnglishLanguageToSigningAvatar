var textarea      = document.getElementById("textToTranslate");
var letterCounter = document.getElementById("inputLabel");

var recordButton       = document.getElementById("recordButton");
var recordInstructions = document.getElementById("recordInstructions");

var bslComboBox  = document.getElementById("bslComboBox");

var isRecording   = false;
var isTranslating = false;

document.getElementById("textTransformed").textContent = "";

textarea.addEventListener("input", function() {
    var text = textarea.value;

    if (text.endsWith("\n")) {
        text = text.slice(0, -1);
        textarea.value = text;

        sendTextToTranslate();
    }

    if (text.length > 50) {
        text = text.substring(0, 50);
        textarea.value = text;
    }

    var textLength = text.length;
    letterCounter.textContent = "Text to translate (" + textLength + "/50): ";
});

function changeLayout() {
    const tableAsRow    = document.querySelector(".tableAsRow");
    const tableAsColumn = document.querySelector(".tableAsColumn");

    if (tableAsRow.style.display === "none") {
        tableAsRow.style.display = "flex";
        tableAsColumn.style.display = "none";
    } else {
        tableAsRow.style.display = "none";
        tableAsColumn.style.display = "flex";
    }
}

function showButton(buttonClass) {
    var button = document.querySelector("." + buttonClass);
    if (button) {
        button.style.display = "block";
    }
}

function hideButton(buttonClass) {
    var button = document.querySelector("." + buttonClass);
    if (button) {
        button.style.display = "none";
    }
}

function updateButtons(isPaused) {
    if (!isTranslating) {
        showButton("buttonPlay");

        hideButton("buttonPause");
        hideButton("buttonContinue");
        hideButton("buttonRestart");
        hideButton("buttonStop");
    } else {
        hideButton("buttonPlay");

        showButton("buttonRestart");
        showButton("buttonStop");

        if (!isPaused) {
            showButton("buttonPause");

            hideButton("buttonContinue");
        } else if (isPaused) {
            showButton("buttonContinue");

            hideButton("buttonPause");
        }
    }

    textarea.disabled     = isTranslating || isRecording;
    recordButton.disabled = isTranslating || isRecording;
    bslComboBox.disabled  = isTranslating || isRecording;

    recordInstructions.textContent = isRecording ? "The recording will stop automatically when you stop talking" : ""
}

function sendTextToTranslate() {
    var text = document.getElementById("textToTranslate").value;
    if (text == "") {
        return false;
    }

    isTranslating = true;
    updateButtons(false);

    var isBSL = bslComboBox.value === "bsl";

    document.getElementById("textTransformed").textContent = "Processing...";
    document.getElementById("processedText").textContent   = "";
    document.querySelector(".txtGloss.av0").value          = "";

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var textInSigml = JSON.parse(this.responseText).textInSigml;

            document.querySelector(".txtaSiGMLText.av0").value = textInSigml;

            var processedText = JSON.parse(this.responseText).processedText;

            document.getElementById("textTransformed").textContent = "Text transformed";
            document.getElementById("processedText").textContent = "[ " + processedText + " ]";

            console.log(processedText)

            handleClickButtonPlay();
        }
    };

    xhttp.open("POST", "/translateText", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("textToTranslate=" + text + "&isBSL=" + isBSL + "&id=translate");

    return false;
}

function handleClickButtonPlay() {
    var buttonPlay = document.querySelector(".bttnPlaySiGMLText.av0");
    buttonPlay.click();

    isTranslating = true;
    var isPaused      = false;

    updateButtons(isPaused);

    return false;
}

function handleClickButtonRestart() {
    var buttonStop = document.querySelector(".bttnStop.av0");
    buttonStop.click();

    setTimeout(handleClickButtonPlay, 500);

    return false;
}

function handleClickButtonPause() {
    var buttonPause = document.querySelector(".bttnSuspend.av0");
    buttonPause.click();

    updateButtons(true);

    return false;
}

function handleClickButtonContinue() {
    var buttonContinue = document.querySelector(".bttnResume.av0");
    buttonContinue.click();

    updateButtons(false);

    return false;
}

function handleClickButtonStop() {
    var buttonStop = document.querySelector(".bttnStop.av0");
    buttonStop.click();

    isTranslating = false;

    updateButtons(false);

    document.getElementById("textTransformed").textContent = "";
    document.getElementById("processedText").textContent   = "";
    document.querySelector(".txtGloss.av0").value          = "";
    return false;
}

function handleSpeed() {
    const value = document.getElementById("speedComboBox").value;

    const bttnSpeedReset = document.querySelector(".bttnSpeedReset.av0");
    bttnSpeedReset.click();

    if (value.includes("-")) {
        const buttonSpeedDown = document.querySelector(".bttnSpeedDown.av0");
        const steps = parseFloat(value.split("-")[1]);
        for (var i = 0; i < steps; i++) {
            buttonSpeedDown.click();
        }
    } else {
        const buttonSpeedUp = document.querySelector(".bttnSpeedUp.av0");
        const steps = parseFloat(value);
        for (var i = 0; i < steps; i++) {
            buttonSpeedUp.click();
        }
    }
}

function transcribe() {
    console.log("le han dado", isRecording)
    var xhttp = new XMLHttpRequest();

    const recordButton = document.getElementById("recordButton");

    recordButton.innerHTML = "<span class='icon'></span>Recording...";

    recordButton.classList.remove('notRecording');
    recordButton.classList.add   ('recording');

    isRecording = true;
    updateButtons(false);

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var transcript = JSON.parse(this.responseText).transcript;
    
                document.getElementById("textToTranslate").value = transcript;
            }

            recordButton.innerHTML = "<span class='icon'></span>Start recording";
    
            recordButton.classList.remove("recording");
            recordButton.classList.add   ("notRecording");

            letterCounter.textContent = "Text to translate (" + transcript.length + "/50): ";

            isRecording = false;
            updateButtons(false);
        }
    };

    xhttp.open("POST", "/translateText", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("id=transcribe");

    return false;
}