function openSpotify(trackId) {
  const appUrl = `spotify:track:${trackId}`;
  const webUrl = `https://open.spotify.com/track/${trackId}`;

  const iframe = document.createElement('iframe');
  iframe.style.display = 'none';
  iframe.src = appUrl;
  document.body.appendChild(iframe);

  setTimeout(() => {
    window.open(webUrl, '_blank');
  }, 3000); // fallback after 3 seconds
}

console.log('Spotify launcher script loaded.');
