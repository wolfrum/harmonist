document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('artist-search');
  const genreCards = document.querySelectorAll('.genre-card');

  if (!searchInput) return;

  searchInput.addEventListener('input', function () {
    const query = this.value.toLowerCase();

    genreCards.forEach((card) => {
      const matches = Array.from(card.querySelectorAll('li')).some((li) =>
        li.textContent.toLowerCase().includes(query)
      );

      card.style.display = matches ? 'block' : 'none';
    });
  });
});
