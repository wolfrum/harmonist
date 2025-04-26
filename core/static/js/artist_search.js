document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('artist-search-input');
  const genreSections = document.querySelectorAll('.genre-section');

  if (!searchInput) return;

  searchInput.addEventListener('input', function () {
    const query = this.value.toLowerCase();

    genreSections.forEach((section) => {
      const matches = Array.from(section.querySelectorAll('.artist-name')).some(
        (el) => el.textContent.toLowerCase().includes(query)
      );

      section.style.display = matches ? 'block' : 'none';
    });
  });
});
