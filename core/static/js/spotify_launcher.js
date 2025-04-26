function openSpotify(trackId) {
  const appUrl = `spotify:track:${trackId}`;
  const webUrl = `https://open.spotify.com/track/${trackId}`;

  // Create an invisible iframe to attempt native app launch
  const iframe = document.createElement('iframe');
  iframe.style.display = 'none';
  iframe.src = appUrl;
  document.body.appendChild(iframe);

  const now = Date.now();

  // If no native response after 1 second, open the web version
  setTimeout(() => {
    if (Date.now() - now < 1200) {
      window.open(webUrl, '_blank');
    }
    document.body.removeChild(iframe);
  }, 1000);
}

// Automatically hook up song links with data-spotify-id
document.addEventListener('DOMContentLoaded', () => {
  const spotifyIcons = document.querySelectorAll('[data-spotify-id]');

  spotifyIcons.forEach((el) => {
    el.addEventListener('click', (event) => {
      event.preventDefault();
      const trackId = el.getAttribute('data-spotify-id');
      if (trackId) {
        openSpotify(trackId);
      }
    });
  });

  console.log('✅ Spotify launcher initialized.');
});
