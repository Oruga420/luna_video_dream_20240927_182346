document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const buttonText = generateBtn.querySelector('.button-text');
    const spinner = generateBtn.querySelector('.spinner');
    const videoContainer = document.getElementById('video-container');
    const generatedVideo = document.getElementById('generated-video');
    const downloadCombinedBtn = document.getElementById('download-combined-btn');
    const downloadAudioBtn = document.getElementById('download-audio-btn');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const inputType = document.getElementById('input-type');
    const imageUploadSection = document.getElementById('image-upload-section');
    const initialImage = document.getElementById('initial-image');
    const urlInput = document.getElementById('url-input');
    const firstLastFrameSection = document.getElementById('first-last-frame-section');
    const firstFrame = document.getElementById('first-frame');
    const lastFrame = document.getElementById('last-frame');
    const soundEffectToggle = document.getElementById('sound-effect-toggle');

    function createStarryBackground() {
        const container = document.body;
        const starCount = 100;
        const stars = [];

        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.top = `${Math.random() * 100}%`;
            star.style.left = `${Math.random() * 100}%`;
            star.style.animationDuration = `${Math.random() * 3 + 2}s`;
            star.style.animationDelay = `${Math.random() * 5}s`;
            container.appendChild(star);
            stars.push(star);
        }

        return stars;
    }

    const stars = createStarryBackground();

    function updateStarColors(isDarkMode) {
        const starColor = isDarkMode ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.3)';
        stars.forEach(star => star.style.backgroundColor = starColor);
    }

    darkModeToggle.addEventListener('change', () => {
        document.body.classList.toggle('dark-mode');
        updateStarColors(darkModeToggle.checked);
        localStorage.setItem('darkMode', darkModeToggle.checked);
    });

    if (localStorage.getItem('darkMode') === 'true') {
        darkModeToggle.checked = true;
        document.body.classList.add('dark-mode');
        updateStarColors(true);
    }

    soundEffectToggle.addEventListener('change', () => {
        localStorage.setItem('soundEffectEnabled', soundEffectToggle.checked);
    });

    if (localStorage.getItem('soundEffectEnabled') === 'false') {
        soundEffectToggle.checked = false;
    }

    document.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;

        stars.forEach(star => {
            const rect = star.getBoundingClientRect();
            const starCenterX = rect.left + rect.width / 2;
            const starCenterY = rect.top + rect.height / 2;

            const deltaX = (mouseX - 0.5) * 20;
            const deltaY = (mouseY - 0.5) * 20;

            star.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
        });
    });

    inputType.addEventListener('change', () => {
        if (inputType.value === 'image_text') {
            imageUploadSection.classList.remove('hidden');
            urlInput.classList.add('hidden');
            firstLastFrameSection.classList.add('hidden');
            promptInput.classList.remove('hidden');
        } else if (inputType.value === 'url') {
            imageUploadSection.classList.add('hidden');
            urlInput.classList.remove('hidden');
            firstLastFrameSection.classList.add('hidden');
            promptInput.classList.remove('hidden');
        } else if (inputType.value === 'first_last_frame') {
            imageUploadSection.classList.add('hidden');
            urlInput.classList.add('hidden');
            firstLastFrameSection.classList.remove('hidden');
            promptInput.classList.remove('hidden');
        } else {
            imageUploadSection.classList.add('hidden');
            urlInput.classList.add('hidden');
            firstLastFrameSection.classList.add('hidden');
            promptInput.classList.remove('hidden');
        }
    });

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();
        const url = urlInput.value.trim();
        if ((!prompt && inputType.value !== 'url') || (inputType.value === 'url' && !url)) {
            showNotification('Please enter a prompt or URL before generating a video.');
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('input_type', inputType.value);
            formData.append('sound_effect_enabled', soundEffectToggle.checked);

            if (inputType.value === 'image_text') {
                if (!initialImage.files[0]) {
                    throw new Error('Please upload an initial image.');
                }
                formData.append('initial_image', initialImage.files[0]);
            } else if (inputType.value === 'url') {
                formData.append('url', url);
            } else if (inputType.value === 'first_last_frame') {
                if (!firstFrame.files[0] || !lastFrame.files[0]) {
                    throw new Error('Please upload both first and last frame images.');
                }
                formData.append('first_frame', firstFrame.files[0]);
                formData.append('last_frame', lastFrame.files[0]);
            }

            const response = await fetch('/generate_video', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to generate video');
            }

            const data = await response.json();
            await loadVideo(data.combined_video_url);
            setupDownloadButtons(data);
            showVideoContainer();
        } catch (error) {
            console.error('Error:', error);
            showNotification(`An error occurred: ${error.message}. Please try again.`);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        buttonText.textContent = isLoading ? 'Generating...' : 'Generate Video';
        spinner.classList.toggle('hidden', !isLoading);
        if (isLoading) {
            videoContainer.classList.add('hidden');
            videoContainer.classList.remove('visible');
        }
    }

    async function loadVideo(url) {
        return new Promise((resolve, reject) => {
            generatedVideo.src = url;
            generatedVideo.onloadeddata = () => {
                console.log('Video loaded successfully');
                resolve();
            };
            generatedVideo.onerror = (error) => {
                console.error('Error loading video:', error);
                reject(new Error('Failed to load video'));
            };
        });
    }

    function setupDownloadButtons(data) {
        if (data.combined_video_url) {
            downloadCombinedBtn.href = data.combined_video_url;
            downloadCombinedBtn.classList.remove('hidden');
        } else {
            downloadCombinedBtn.classList.add('hidden');
        }
        if (data.separate_audio_url) {
            downloadAudioBtn.href = data.separate_audio_url;
            downloadAudioBtn.classList.remove('hidden');
        } else {
            downloadAudioBtn.classList.add('hidden');
        }
    }

    function showVideoContainer() {
        videoContainer.classList.remove('hidden');
        setTimeout(() => {
            videoContainer.classList.add('visible');
            generatedVideo.play().catch(error => {
                console.error('Error playing video:', error);
                showNotification('Error playing video. Please try again.');
            });
        }, 50);
        videoContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        notification.style.color = 'white';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '1000';
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }

    [downloadCombinedBtn, downloadAudioBtn].forEach(btn => {
        btn.addEventListener('click', (e) => {
            const originalText = btn.textContent;
            btn.textContent = 'Downloading...';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 3000);
        });
    });

    const elements = document.querySelectorAll('button, textarea, .download-btn, select, input[type="file"]');
    elements.forEach(element => {
        element.addEventListener('mouseover', () => {
            element.style.transition = 'transform 0.3s ease';
            element.style.transform = 'scale(1.05)';
        });
        element.addEventListener('mouseout', () => {
            element.style.transform = 'scale(1)';
        });
    });

    promptInput.addEventListener('focus', () => {
        promptInput.style.transition = 'transform 0.3s ease';
        promptInput.style.transform = 'scale(1.02)';
    });
    promptInput.addEventListener('blur', () => {
        promptInput.style.transform = 'scale(1)';
    });
});
