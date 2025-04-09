document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-connections');
  const fallback = document.getElementById('network-fallback');

  if (toggleBtn && fallback) {
    toggleBtn.addEventListener('click', () => {
      fallback.classList.toggle('hidden');
      toggleBtn.textContent = fallback.classList.contains('hidden')
        ? 'Show all connections'
        : 'Hide connections';
    });
  }
});
