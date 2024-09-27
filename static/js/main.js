document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const loading = document.getElementById('loading');
    const videoContainer = document.getElementById('video-container');
    const generatedVideo = document.getElementById('generated-video');
    const downloadBtn = document.getElementById('download-btn');

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a prompt before generating a video.');
            return;
        }

        loading.textContent = 'Generating video...';
        loading.classList.remove('hidden');
        videoContainer.classList.add('hidden');
        downloadBtn.classList.add('hidden');
        generateBtn.disabled = true;

        try {
            const response = await fetch('/generate_video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate video');
            }

            const data = await response.json();
            generatedVideo.src = data.video_url;
            
            // Ensure video is loaded before displaying
            generatedVideo.onloadeddata = () => {
                videoContainer.classList.remove('hidden');
                generatedVideo.style.height = 'auto';
                
                // Set up download button
                downloadBtn.href = data.video_url;
                downloadBtn.download = 'generated_video.mp4';
                downloadBtn.classList.remove('hidden');
                downloadBtn.textContent = 'Download Video';
            };
            
            generatedVideo.onerror = () => {
                throw new Error('Failed to load video');
            };
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}. Please try again.`);
        } finally {
            loading.classList.add('hidden');
            generateBtn.disabled = false;
        }
    });

    // Add loading indicator for download button
    downloadBtn.addEventListener('click', () => {
        downloadBtn.textContent = 'Downloading...';
        setTimeout(() => {
            downloadBtn.textContent = 'Download Video';
        }, 3000); // Reset after 3 seconds
    });
});
