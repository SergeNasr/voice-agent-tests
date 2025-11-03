import { startAudioCapture, stopAudioCapture } from '/static/audio.js';

let websocket = null;
let isConversationActive = false;

const conversationBtn = document.getElementById('conversationBtn');
const transcriptionDiv = document.getElementById('transcription');

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

function updateButton(isActive) {
    if (isActive) {
        conversationBtn.textContent = 'Stop Conversation';
    } else {
        conversationBtn.textContent = 'Start Conversation';
    }
}

async function startConversation() {
    console.log('Starting conversation...');
    
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
        console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
        if (typeof event.data === 'string') {
            const message = JSON.parse(event.data);
            
            if (message.type === 'connected') {
                console.log('Connected to provider:', message.provider);
            } else if (message.type === 'transcription') {
                console.log('Transcription received:', message.text);
                transcriptionDiv.textContent += message.text + ' ';
            } else if (message.type === 'error') {
                console.error('Error:', message.message);
            }
        }
    };
    
    websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
        console.log('WebSocket closed');
        stopConversation();
    };
    
    await new Promise((resolve) => {
        if (websocket.readyState === WebSocket.OPEN) {
            resolve();
        } else {
            websocket.onopen = () => resolve();
        }
    });
    
    await startAudioCapture((audioChunk) => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(audioChunk);
        }
    });
    
    isConversationActive = true;
    updateButton(true);
    console.log('Conversation started');
}

function stopConversation() {
    console.log('Stopping conversation...');
    
    stopAudioCapture();
    
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    
    isConversationActive = false;
    updateButton(false);
    console.log('Conversation stopped');
}

conversationBtn.addEventListener('click', () => {
    if (isConversationActive) {
        stopConversation();
    } else {
        startConversation();
    }
});
