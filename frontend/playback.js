let playbackContext = null;

function initPlaybackContext() {
    if (!playbackContext) {
        playbackContext = new AudioContext({ sampleRate: 16000 });
    }
    return playbackContext;
}

async function playPCM16Audio(pcm16Data, sampleRate = 16000) {
    const context = initPlaybackContext();
    
    const audioBuffer = context.createBuffer(1, pcm16Data.length / 2, sampleRate);
    const channelData = audioBuffer.getChannelData(0);
    const int16Array = new Int16Array(pcm16Data);
    
    for (let i = 0; i < channelData.length; i++) {
        channelData[i] = int16Array[i] / 32768.0;
    }
    
    const source = context.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(context.destination);
    source.start();
}

export { playPCM16Audio };
