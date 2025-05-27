window.addEventListener('DOMContentLoaded', () => {
    const cameraFeed = document.getElementById('camera-feed');
    const startButton = document.getElementById('start-camera-btn');
    const statusIndicator = document.getElementById('status-indicator');
    const loadingOverlay = document.getElementById('loading-overlay');
    const imageAnalysisCircles = document.querySelectorAll('#image-analysis-circles-container .image-circle-item img');
    const progressTexts = document.querySelectorAll('#image-analysis-circles-container .analysis-progress-text');
    const llmOutputDisplay = document.getElementById('llm-output-display');

    // Helper function to reset UI to initial state
    function resetUI() {
        if (statusIndicator) {
            statusIndicator.textContent = 'NOT RECORDING';
            statusIndicator.classList.remove('recording');
            statusIndicator.style.backgroundColor = ''; // Revert to CSS default
        }
        if (startButton) {
            startButton.style.display = 'block';
            startButton.disabled = false;
        }
        if (cameraFeed) {
            cameraFeed.style.filter = 'brightness(1)';
            if (cameraFeed.srcObject) { // If a stream exists, stop it
                cameraFeed.srcObject.getTracks().forEach(track => track.stop());
                cameraFeed.srcObject = null;
            }
        }
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        imageAnalysisCircles.forEach(img => img.src = 'https://via.placeholder.com/80x80?text=Frame'); // Reset placeholder
        progressTexts.forEach(text => text.textContent = '0%');
        if (llmOutputDisplay) {
            llmOutputDisplay.innerHTML = '<p>LLM analysis results will appear here...</p>';
        }
    }
    
    if (startButton && cameraFeed && statusIndicator && loadingOverlay && imageAnalysisCircles.length > 0 && progressTexts.length > 0 && llmOutputDisplay) {
        resetUI(); // Set initial state

        startButton.addEventListener('click', async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
                cameraFeed.srcObject = stream;
                
                // Wait for video metadata to load to get correct dimensions
                cameraFeed.onloadedmetadata = () => {
                    statusIndicator.textContent = 'RECORDING...';
                    statusIndicator.classList.add('recording');
                    statusIndicator.style.backgroundColor = ''; // Let CSS class handle it

                    startButton.style.display = 'none'; // Hide start button
                    
                    startFrameCapture(stream);
                };

            } catch (error) {
                console.error('Error accessing camera:', error);
                statusIndicator.textContent = 'CAMERA ERROR';
                statusIndicator.classList.remove('recording');
                statusIndicator.style.backgroundColor = 'red';

                if (error.name === 'NotAllowedError') {
                    alert('Camera access was denied. Please enable camera permissions in your browser/system settings.');
                } else if (error.name === 'NotFoundError') {
                    alert('No camera found. Please ensure a camera is connected and enabled.');
                } else {
                    alert('An error occurred while accessing the camera: ' + error.message);
                }
                resetUI(); // Reset UI on error
            }
        });
    } else {
        console.error('One or more required HTML elements are missing.');
        if (!startButton) console.error('Start button not found');
        if (!cameraFeed) console.error('Camera feed element not found');
        if (!statusIndicator) console.error('Status indicator element not found');
        if (!loadingOverlay) console.error('Loading overlay not found');
        if (imageAnalysisCircles.length === 0) console.error('Image analysis circles not found');
        if (progressTexts.length === 0) console.error('Progress texts not found');
        if (!llmOutputDisplay) console.error('LLM output display not found');
    }

    function startFrameCapture(stream) {
        const canvas = document.createElement('canvas');
        // Dimensions will be set once video is playing and metadata is loaded
        const context = canvas.getContext('2d');
        const capturedFrames = [];
        let framesCaptured = 0;
        const captureIntervalMs = 800; // Capture a frame every 800ms
        const totalFramesToCapture = 5;

        const intervalId = setInterval(() => {
            // Ensure video is ready and playing to get dimensions
            if (framesCaptured < totalFramesToCapture && cameraFeed.readyState >= cameraFeed.HAVE_METADATA && cameraFeed.videoWidth > 0) {
                if (canvas.width !== cameraFeed.videoWidth || canvas.height !== cameraFeed.videoHeight) {
                    canvas.width = cameraFeed.videoWidth;
                    canvas.height = cameraFeed.videoHeight;
                }

                context.drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL('image/jpeg');
                capturedFrames.push(dataUrl);
                framesCaptured++;

                if (imageAnalysisCircles[framesCaptured - 1]) {
                    imageAnalysisCircles[framesCaptured - 1].src = dataUrl;
                }
                if (progressTexts[framesCaptured - 1]) {
                    progressTexts[framesCaptured - 1].textContent = 'Captured';
                }

                if (framesCaptured === totalFramesToCapture) {
                    clearInterval(intervalId);
                    processCapturedFrames(capturedFrames, stream);
                }
            }
        }, captureIntervalMs);
    }

    function processCapturedFrames(frames, stream) {
        stream.getTracks().forEach(track => track.stop());
        cameraFeed.srcObject = null;
        cameraFeed.style.filter = 'brightness(0.5)'; // Dim the camera feed area

        if (statusIndicator) {
            statusIndicator.textContent = 'ANALYZING...';
            statusIndicator.classList.remove('recording');
            statusIndicator.style.backgroundColor = '#f39c12'; // Orange
        }

        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }

        frames.forEach((frameData, index) => {
            console.log(`Simulating analysis for frame ${index + 1}`);
            setTimeout(() => {
                if (progressTexts[index]) {
                    progressTexts[index].textContent = `${Math.floor(Math.random() * 50) + 50}%`;
                }
                
                const circleItem = imageAnalysisCircles[index].closest('.image-circle-item');
                if (circleItem) {
                    const shimmer = circleItem.querySelector('.loading-shimmer');
                    if (shimmer) {
                        // The CSS animation is infinite, so it should be running.
                        // If it needed to be explicitly started: shimmer.style.animationPlayState = 'running';
                        // Or add a class that triggers it. For now, we assume CSS handles it.
                    }
                }

                if (index === frames.length - 1) {
                    setTimeout(() => {
                        if (loadingOverlay) loadingOverlay.style.display = 'none';
                        if (cameraFeed) cameraFeed.style.filter = 'brightness(1)';
                        
                        if (statusIndicator) {
                            statusIndicator.textContent = 'ANALYSIS COMPLETE';
                            statusIndicator.style.backgroundColor = '#2ecc71'; // Green
                        }

                        if (llmOutputDisplay) {
                            llmOutputDisplay.innerHTML = '<p>Analysis complete. Results would show here.</p>';
                        }
                        
                        // Option to re-enable start button or offer a "restart"
                        // For now, just log and user can refresh to restart
                        console.log("Analysis complete. UI ready for new interaction if restart logic is added.");
                        // startButton.style.display = 'block'; // Example: Show start button again
                        // resetUI(); // Or call resetUI to put everything back to initial state
                        
                    }, 2000); // Simulate time for overall analysis result
                }
            }, (index + 1) * 1000); // Stagger simulated progress updates
        });
    }
});
