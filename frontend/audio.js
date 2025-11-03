const SAMPLE_RATE = 16000;
const CHUNK_SIZE = 4096;

let audioContext = null;
let sourceNode = null;
let processorNode = null;
let mediaStream = null;
let onChunkCallback = null;

function encodePCM16(float32Array) {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
        const s = Math.max(-1, Math.min(1, float32Array[i]));
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array.buffer;
}

async function startAudioCapture(onChunk) {
    console.log('Starting audio capture...');

    onChunkCallback = onChunk;

    mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
            channelCount: 1,
            sampleRate: SAMPLE_RATE,
            echoCancellation: true,
            noiseSuppression: true,
        }
    });

    console.log('Microphone access granted');

    audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
    sourceNode = audioContext.createMediaStreamSource(mediaStream);

    processorNode = audioContext.createScriptProcessor(CHUNK_SIZE, 1, 1);

    processorNode.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        const pcm16Buffer = encodePCM16(inputData);

        if (onChunkCallback && audioContext.state === 'running') {
            onChunkCallback(pcm16Buffer);
        }
    };

    sourceNode.connect(processorNode);
    processorNode.connect(audioContext.destination);

    console.log('Audio capture started');
}

function stopAudioCapture() {
    console.log('Stopping audio capture...');

    if (processorNode) {
        processorNode.disconnect();
        processorNode = null;
    }

    if (sourceNode) {
        sourceNode.disconnect();
        sourceNode = null;
    }

    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }

    onChunkCallback = null;

    console.log('Audio capture stopped');
}

export { startAudioCapture, stopAudioCapture };
