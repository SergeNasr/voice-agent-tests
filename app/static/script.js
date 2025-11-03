let websocket = null;
let mediaRecorder = null;
let audioStream = null;
let isCallActive = false;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusDiv = document.getElementById('status');
const transcriptionDiv = document.getElementById('transcription');

// Get WebSocket URL
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

async function startCall() {
    try {
        // Request microphone access
        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true,
            }
        });

        // Connect WebSocket
        websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
            console.log('WebSocket connected');
            updateStatus('Connected', 'connected');
        };

        websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);

            if (message.type === 'transcription') {
                // Append transcription
                transcriptionDiv.textContent += message.text + ' ';
            } else if (message.type === 'connected') {
                console.log(`Connected to provider: ${message.provider}`);
            } else if (message.type === 'error') {
                console.error('Error:', message.message);
                alert(`Error: ${message.message}`);
            }
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('Connection Error', '');
        };

        websocket.onclose = () => {
            console.log('WebSocket closed');
            updateStatus('Disconnected', '');
            endCall();
        };

        // Wait for WebSocket to be ready
        await new Promise((resolve) => {
            if (websocket.readyState === WebSocket.OPEN) {
                resolve();
            } else {
                websocket.onopen = () => resolve();
            }
        });

        // Setup MediaRecorder
        const options = {
            mimeType: 'audio/webm;codecs=opus',
            audioBitsPerSecond: 16000,
        };

        // Fallback to default if codec not supported
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options.mimeType = 'audio/webm';
        }

        mediaRecorder = new MediaRecorder(audioStream, options);

        mediaRecorder.ondataavailable = async (event) => {
            if (event.data.size > 0 && websocket && websocket.readyState === WebSocket.OPEN) {
                // Convert Blob to ArrayBuffer then to bytes
                const arrayBuffer = await event.data.arrayBuffer();
                websocket.send(arrayBuffer);
            }
        };

        // Start recording with 250ms chunks for low latency
        mediaRecorder.start(250);
        isCallActive = true;

        updateStatus('Call Active', 'recording');
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';

    } catch (error) {
        console.error('Error starting call:', error);
        alert(`Error: ${error.message}`);
        updateStatus('Error', '');
        // Reset button visibility on error
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
        isCallActive = false;
    }
}

function endCall() {
    if (mediaRecorder && isCallActive) {
        mediaRecorder.stop();
        isCallActive = false;
    }

    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }

    if (websocket) {
        websocket.close();
        websocket = null;
    }

    updateStatus('Disconnected', '');
    startBtn.style.display = 'block';
    stopBtn.style.display = 'none';
}

function updateStatus(text, className) {
    statusDiv.textContent = text;
    statusDiv.className = `status ${className}`;
}

// Event listeners
startBtn.addEventListener('click', startCall);
stopBtn.addEventListener('click', endCall);

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    endCall();
});

