// Initialize Lucide icons
lucide.createIcons();

const API_BASE = 'http://127.0.0.1:5000';

// Language selector
const langSelect = document.getElementById('lang-select');
const getLang = () => langSelect ? langSelect.value : 'en';

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const removeImageBtn = document.getElementById('remove-image');
const diseaseResult = document.getElementById('disease-result');
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

let currentFile = null;

// ─────────────────────────────────────────────────────────
// IMAGE UPLOAD & DIAGNOSIS
// ─────────────────────────────────────────────────────────

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
});

removeImageBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    previewContainer.classList.add('hidden');
    dropZone.classList.remove('hidden');
    diseaseResult.classList.add('hidden');
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file (JPG/PNG).');
        return;
    }
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        dropZone.classList.add('hidden');
        previewContainer.classList.remove('hidden');
        analyzeImage(file);
    };
    reader.readAsDataURL(file);
}

// ─────────────────────────────────────────────────────────
// CHAT HELPERS
// ─────────────────────────────────────────────────────────

function appendMessage(sender, text, isMarkdown = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + sender;
    const icon = sender === 'user' ? 'user' : 'bot';
    let formattedText = text;
    if (isMarkdown) {
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formattedText = formattedText.replace(/\n/g, '<br>');
    }
    msgDiv.innerHTML = '<div class="avatar"><i data-lucide="' + icon + '"></i></div><div class="bubble">' + formattedText + '</div>';
    chatBox.appendChild(msgDiv);
    lucide.createIcons({ root: msgDiv });
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message system typing';
    msgDiv.id = 'typing-indicator';
    msgDiv.innerHTML = '<div class="avatar"><i data-lucide="bot"></i></div><div class="bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
    chatBox.appendChild(msgDiv);
    lucide.createIcons({ root: msgDiv });
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

// ─────────────────────────────────────────────────────────
// IMAGE ANALYSIS
// ─────────────────────────────────────────────────────────

async function analyzeImage(file) {
    appendMessage('user', '<em>Uploaded an image for diagnosis.</em>', true);
    showTyping();
    try {
        const formData = new FormData();
        formData.append('image', file);
        const res = await fetch(API_BASE + '/analyze', { method: 'POST', body: formData });
        const data = await res.json();
        hideTyping();
        if (data.status === 'success') {
            const d = data.disease;
            document.getElementById('res-plant').textContent = d.plant || 'Unknown';
            document.getElementById('res-disease').textContent = d.disease || 'Unknown';
            document.getElementById('res-confidence').textContent = d.confidence ? d.confidence + '%' : '-';
            document.getElementById('res-disease').className = (d.disease && d.disease.toLowerCase() !== 'healthy') ? 'value highlight' : 'value healthy';
            diseaseResult.classList.remove('hidden');
            appendMessage('system', data.advice, true);
        } else {
            appendMessage('system', 'Error: ' + (data.message || 'Analysis failed.'));
        }
    } catch (err) {
        hideTyping();
        appendMessage('system', 'Connection Error: Make sure the Flask API is running on ' + API_BASE + '.');
    }
}

// ─────────────────────────────────────────────────────────
// TEXT CHAT
// ─────────────────────────────────────────────────────────

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;
    chatInput.value = '';
    appendMessage('user', query);
    showTyping();
    try {
        const res = await fetch(API_BASE + '/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, lang: getLang() })
        });
        const data = await res.json();
        hideTyping();
        if (data.status === 'success') {
            appendMessage('system', data.advice, true);
        } else {
            appendMessage('system', 'Error: ' + (data.message || 'Failed to get advice.'));
        }
    } catch (err) {
        hideTyping();
        appendMessage('system', 'Connection Error: Make sure the Flask API is running on ' + API_BASE + '.');
    }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

// ─────────────────────────────────────────────────────────
// TAB SWITCHING
// ─────────────────────────────────────────────────────────

function switchTab(tab) {
    document.getElementById('panel-text').classList.toggle('hidden', tab !== 'text');
    document.getElementById('panel-voice').classList.toggle('hidden', tab !== 'voice');
    document.getElementById('tab-text').classList.toggle('active', tab === 'text');
    document.getElementById('tab-voice').classList.toggle('active', tab === 'voice');
    lucide.createIcons();
}

// ─────────────────────────────────────────────────────────
// VOICE ASSISTANT  —  Web Speech API (browser-native STT)
//
// Flow:
//   1. Hold mic button  → browser listens & transcribes words in real-time
//   2. Release          → send transcribed text to /ask for AI advisory
//   3. Display response → read it aloud via browser SpeechSynthesis
//
// No file upload, no Gemini quota consumed for STT.
// ─────────────────────────────────────────────────────────

const micBtn          = document.getElementById('mic-btn');
const micHint         = document.getElementById('mic-hint');
const voiceStatus     = document.getElementById('voice-status');
const voiceStatusText = document.getElementById('voice-status-text');
const transcriptBox   = document.getElementById('voice-transcript-box');
const transcriptText  = document.getElementById('voice-transcript-text');
const responseBox     = document.getElementById('voice-response-box');
const responseText    = document.getElementById('voice-response-text');
const audioPlayer     = document.getElementById('voice-audio-player');
const askAgainBtn     = document.getElementById('ask-again-btn');
const stopSpeakBtn    = document.getElementById('stop-speak-btn');
const pauseResumeBtn  = document.getElementById('pause-resume-btn');
const pauseIcon       = document.getElementById('pause-icon');
const pauseText       = document.getElementById('pause-text');

// Map language code → BCP-47 tag for SpeechRecognition & SpeechSynthesis
const SPEECH_LANG_MAP = {
    en: 'en-IN', hi: 'hi-IN', pa: 'pa-IN', mr: 'mr-IN',
    ta: 'ta-IN', te: 'te-IN', gu: 'gu-IN', kn: 'kn-IN',
};

let recognition  = null;
let isListening  = false;
let finalText    = '';
let interimText  = '';    // fallback when stop() fires before isFinal
let stopTimer    = null;  // debounce timer for stopping recognition

function setVoiceStatus(text, type) {
    voiceStatusText.textContent = text;
    voiceStatus.className = 'voice-status' + (type ? ' ' + type : '');
}

function buildRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;

    const r = new SR();
    r.continuous      = false;
    r.interimResults  = true;
    r.maxAlternatives = 1;
    r.lang            = SPEECH_LANG_MAP[getLang()] || 'en-IN';

    // Show words as user speaks (interim + final)
    r.onresult = (e) => {
        interimText = '';
        finalText   = '';
        for (const res of e.results) {
            if (res.isFinal) finalText  += res[0].transcript;
            else             interimText += res[0].transcript;
        }
        // Display whichever is available (interim updates live)
        transcriptText.textContent = finalText || interimText;
        transcriptBox.classList.remove('hidden');
    };

    // When speech ends — use finalText, else fall back to interimText
    r.onend = () => {
        isListening = false;
        micBtn.classList.remove('recording');
        document.getElementById('mic-icon').setAttribute('data-lucide', 'mic');
        lucide.createIcons({ root: micBtn });

        // Use finalText first; fall back to last interim if stop() fired too early
        const said = (finalText || interimText || '').trim();
        if (said) {
            transcriptText.textContent = said;  // lock in what was heard
            micHint.textContent = 'Getting answer...';
            setVoiceStatus('Getting AI advice...', 'active');
            getAdviceForText(said);
        } else {
            setVoiceStatus('Nothing captured — speak louder or hold longer', 'error');
            micHint.textContent = 'Press & hold the mic to speak';
        }
    };

    r.onerror = (e) => {
        isListening = false;
        micBtn.classList.remove('recording');
        document.getElementById('mic-icon').setAttribute('data-lucide', 'mic');
        lucide.createIcons({ root: micBtn });
        const msg = e.error === 'not-allowed' ? 'Microphone access denied' : 'Error: ' + e.error;
        setVoiceStatus(msg, 'error');
        micHint.textContent = 'Press & hold the mic to speak';
    };

    return r;
}

function startListening() {
    if (isListening) return;

    // Clear previous session
    finalText   = '';
    interimText = '';
    transcriptText.textContent = '';
    transcriptBox.classList.add('hidden');
    responseBox.classList.add('hidden');
    audioPlayer.src = '';
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    if (stopTimer) { clearTimeout(stopTimer); stopTimer = null; }
    stopSpeakBtn.classList.add('hidden');
    pauseResumeBtn.classList.add('hidden');

    recognition = buildRecognition();
    if (!recognition) {
        setVoiceStatus('Speech recognition not supported. Use Chrome or Edge.', 'error');
        return;
    }

    try {
        recognition.start();
        isListening = true;
        micBtn.classList.add('recording');
        micHint.textContent = 'Listening... click mic again to stop';
        setVoiceStatus('Listening...', 'active');
        document.getElementById('mic-icon').setAttribute('data-lucide', 'mic-off');
        lucide.createIcons({ root: micBtn });
    } catch(e) {
        setVoiceStatus('Could not start microphone', 'error');
    }
}

function stopListening() {
    if (!recognition || !isListening) return;
    // Small delay so recognition can finalize the last word before stopping.
    // Without this, releasing the button mid-word loses the interim transcript.
    stopTimer = setTimeout(() => {
        try { recognition.stop(); } catch(_) {}
        stopTimer = null;
    }, 400);
}

async function getAdviceForText(text) {
    try {
        // 1. Send transcribed words to /ask endpoint
        const res  = await fetch(API_BASE + '/ask', {
            method : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body   : JSON.stringify({ query: text, lang: getLang() })
        });
        const data = await res.json();

        if (data.status !== 'success') {
            setVoiceStatus(data.message || 'Advisory failed', 'error');
            micHint.textContent = 'Press & hold the mic to speak';
            return;
        }

        const advice = data.advice || '';

        // 2. Show advice text
        responseText.innerHTML = advice
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        responseBox.classList.remove('hidden');

        // ── 3. Read response aloud via browser TTS (works in all languages, zero latency)
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(advice.replace(/\*\*/g, ''));
            utterance.lang  = SPEECH_LANG_MAP[getLang()] || 'en-IN';
            utterance.rate  = 0.92;
            utterance.pitch = 1;

            utterance.onstart = () => {
                stopSpeakBtn.classList.remove('hidden');
                pauseResumeBtn.classList.remove('hidden');
                updatePauseUI(false); // ensure it shows 'Pause' initially
                lucide.createIcons({ root: stopSpeakBtn });
                lucide.createIcons({ root: pauseResumeBtn });
            };
            utterance.onend = () => {
                stopSpeakBtn.classList.add('hidden');
                pauseResumeBtn.classList.add('hidden');
            };
            utterance.onerror = () => {
                stopSpeakBtn.classList.add('hidden');
                pauseResumeBtn.classList.add('hidden');
            };

            window.speechSynthesis.speak(utterance);
        }

        setVoiceStatus('Response ready', '');
        micHint.textContent = 'Click the mic to start speaking';
        askAgainBtn.classList.remove('hidden');
        lucide.createIcons({ root: askAgainBtn });

    } catch (err) {
        setVoiceStatus('Connection error — is the server running?', 'error');
        micHint.textContent = 'Click the mic to start speaking';
        console.error(err);
    }
}

function resetVoicePanel() {
    // Clear all voice UI back to initial state
    finalText   = '';
    interimText = '';
    transcriptText.textContent = '';
    responseText.innerHTML     = '';
    audioPlayer.src            = '';
    transcriptBox.classList.add('hidden');
    responseBox.classList.add('hidden');
    askAgainBtn.classList.add('hidden');
    stopSpeakBtn.classList.add('hidden');
    pauseResumeBtn.classList.add('hidden');
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setVoiceStatus('Ready', '');
    micHint.textContent = 'Click the mic to start speaking';
}

function stopSpeaking() {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
    stopSpeakBtn.classList.add('hidden');
    pauseResumeBtn.classList.add('hidden');
}

function togglePauseResume() {
    if (!window.speechSynthesis) return;

    if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        updatePauseUI(false);
    } else if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        updatePauseUI(true);
    }
}

function updatePauseUI(isPaused) {
    if (isPaused) {
        pauseIcon.setAttribute('data-lucide', 'play');
        pauseText.textContent = 'Resume';
    } else {
        pauseIcon.setAttribute('data-lucide', 'pause');
        pauseText.textContent = 'Pause';
    }
    lucide.createIcons({ root: pauseResumeBtn });
}

// Click-to-toggle mic (one click starts, next click stops)
// This avoids the permission-dialog race where releasing the button
// during the browser "Allow microphone?" prompt would immediately stop listening.
if (micBtn) {
    micBtn.addEventListener('click', () => {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    });
    // Mobile long-press still works via touchend toggle
    micBtn.addEventListener('touchend', (e) => {
        e.preventDefault();
        if (isListening) stopListening();
        else startListening();
    });
}
