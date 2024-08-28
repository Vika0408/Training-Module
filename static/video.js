document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('training-video');
    const progressBar = document.getElementById('progress');
    const nextButton = document.getElementById('next-video');
    const userId = 1;  // Replace with actual user ID dynamically if needed
    const videoId = parseInt(window.location.pathname.split('/').pop()) || 1;  // Get video ID from URL or default to 1

    let progressSaved = false;

    // Load last watched time
    fetch('/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        video.currentTime = data.last_watched || 0;  // Default to 0 if no progress found
    });

    // Save progress on pause
    video.addEventListener('pause', function () {
        if (!progressSaved) {
            fetch('/save_progress', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, video_id: videoId, last_watched: video.currentTime })
            });
            progressSaved = true;
        }
    });

    // Update progress bar
    video.addEventListener('timeupdate', function () {
        const percent = (video.currentTime / video.duration) * 100;
        progressBar.style.width = percent + '%';
    });

    // Prevent fast-forwarding or skipping
    video.addEventListener('seeking', function () {
        if (video.currentTime > video.lastPosition) {
            video.currentTime = video.lastPosition;
        }
    });

    video.addEventListener('timeupdate', function () {
        video.lastPosition = video.currentTime;
    });

    // Handle Next Video button
    document.getElementById('next-video').addEventListener('click', function () {
        const currentVideoId = parseInt(window.location.pathname.split('/').pop()) || 1;
        const nextVideoId = currentVideoId + 1;
        window.location.href = '/play/' + nextVideoId;
    });

    // Enable next video button only after the video is completed
    video.addEventListener('ended', function () {
        nextButton.disabled = false;
    });
});
