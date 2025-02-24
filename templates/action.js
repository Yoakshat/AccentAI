let sentence = "{{sent}}"
let audio = new Audio("static/output.mp3")
let voice_audio = new Audio("static/voice.mp3")

// document.getElementById('audioPlayer').style.display = 'none'; 

document.getElementById('playButton').addEventListener('click', function() {
    // let audio = new Audio("static/output.mp3")
    audio.play().then(() => {
        // Audio is playing
    }).catch((error) => {
        console.error('Error playing audio:', error);
    });
});

audio.addEventListener('ended', function() {
    // Show the input box after audio ends
    showInputBox()
});

// fetch the next sentence and update fields
document.getElementById('next').addEventListener('click', function(){
    // change the sent variable 
    fetch('/next_sentence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({lang: "{{language}}"})
    })
    .then(response => {
        console.log('Response received:', response);

        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json(); // Parse the JSON from the response
    })
    .then(data => {
        sentence = data 
        // change div sentence-display
        document.querySelector(".sentence-display").textContent = data
        // to prevent caching 
        audioUrl = "static/output.mp3?v=" + new Date().getTime();
        audio = new Audio(audioUrl)
        // add the event listener back
        audio.addEventListener('ended', function() {
            // Show the input box after audio ends
            showInputBox()
        });
        // reset this too
        document.getElementById('inputBox').style.display = 'none'; 
    })
})


    document.getElementById('inputBox').addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) { // Check for Enter key without Shift
        event.preventDefault(); // Prevent newline
        processUserInput(); // Process input
    }
});

function processUserInput(){
    // input
    // const userInput = document.getElementById('inputBox').value;
    const userInput = document.getElementById('difficulties').value;

    // Send input to Flask backend
    fetch('/process_input', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: userInput, sentence: sentence})
    })
    .then(response => {
        if(response.status == 204){
            // once chatgpt response is fetched, play the audio 
            // have to make sure doesn't cache
            voiceAudioUrl = "static/voice.mp3?v=" + new Date().getTime();
            voice_audio = new Audio(voiceAudioUrl); // Provide path to your audio file
            voice_audio.play().catch(error => console.error('Audio playback failed:', error)); 
            document.getElementById('difficulties').value = ''; 
        } else {
            throw new Error('Network response was not ok');
        }
    })

    document.getElementById('inputBox').style.display = 'none'; 
}

function showInputBox() {
    document.getElementById('inputBox').style.display = 'block'; // Show the input box
}