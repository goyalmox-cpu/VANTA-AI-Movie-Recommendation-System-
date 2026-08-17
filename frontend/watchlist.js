document.addEventListener('DOMContentLoaded', () => {
  const watchlistGrid = document.getElementById('watchlistGrid');
  const emptyState = document.getElementById('empty-state');
  const vaultStats = document.getElementById('vault-stats');
  const totalSavedCount = document.getElementById('total-saved-count');
  const navWatchlistCount = document.getElementById('nav-watchlist-count');
  const clearAllBtn = document.getElementById('clear-all-btn');

  renderWatchlist();

  if (clearAllBtn) {
    clearAllBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to clear your entire watchlist?')) {
        localStorage.setItem('vanta_watchlist', JSON.stringify([]));
        renderWatchlist();
      }
    });
  }

  function getWatchlist() {
    try {
      return JSON.parse(localStorage.getItem('vanta_watchlist')) || [];
    } catch {
      return [];
    }
  }

  function saveWatchlist(list) {
    localStorage.setItem('vanta_watchlist', JSON.stringify(list));
  }

  function renderWatchlist() {
    const list = getWatchlist();
    const count = list.length;

    if (navWatchlistCount) navWatchlistCount.textContent = count;
    if (totalSavedCount) totalSavedCount.textContent = count;

    if (count === 0) {
      watchlistGrid.classList.add('hidden');
      vaultStats.classList.add('hidden');
      emptyState.classList.remove('hidden');
      watchlistGrid.replaceChildren();
      return;
    }

    emptyState.classList.add('hidden');
    vaultStats.classList.remove('hidden');
    watchlistGrid.classList.remove('hidden');
    watchlistGrid.replaceChildren();

    const gradientPresets = [
      'from-slate-900 via-indigo-950 to-black',
      'from-neutral-900 via-zinc-900 to-black',
      'from-stone-900 via-neutral-950 to-black',
      'from-blue-950 via-slate-900 to-black',
      'from-purple-950 via-slate-950 to-black'
    ];

    list.forEach((film, index) => {
      const card = document.createElement('div');
      card.className = 'movie-card group bg-surface-container-low stagger-fade-in aspect-[2/3] relative card-exit';
      card.style.animationDelay = `${index * 0.08}s`;

      const preset = gradientPresets[index % gradientPresets.length];
      const genresHtml = (film.genres || []).slice(0, 2).map(g =>
        `<span class="bg-surface-container-high/90 text-on-surface px-2 py-0.5 rounded-full font-label text-[10px] uppercase tracking-wider">${g}</span>`
      ).join('');

      const ratingBadge = film.rating
        ? `<span class="bg-secondary/20 text-secondary border border-secondary/30 px-2 py-0.5 rounded-full font-label text-[10px] flex items-center gap-0.5">★ ${film.rating}</span>`
        : '';

      const yearBadge = film.year
        ? `<span class="bg-surface-container-high/90 text-on-surface-variant px-2 py-0.5 rounded-full font-label text-[10px]">${film.year}</span>`
        : '';

      const posterContent = film.poster_url
        ? `<img src="${film.poster_url}" alt="${film.title}" class="w-full h-full object-cover" loading="lazy" />`
        : `<div class="w-full h-full bg-gradient-to-br ${preset} p-4 flex flex-col justify-between border border-white/5">
             <span class="font-label text-xs text-secondary/60">#${String(index + 1).padStart(2, '0')}</span>
             <div>
               <h4 class="font-display font-semibold text-lg text-white mb-1 leading-tight">${film.title}</h4>
               <p class="font-label text-xs text-on-surface-variant">${film.year || ''}</p>
             </div>
           </div>`;

      card.innerHTML = `
        <div class="movie-card-img-wrapper">
          ${posterContent}
        </div>
        <div class="movie-card-overlay">
          <div class="movie-card-content flex flex-col gap-2.5">
            <div class="flex flex-wrap gap-1.5 mb-1">
              ${genresHtml}
              ${yearBadge}
              ${ratingBadge}
            </div>
            <h3 class="font-display font-semibold text-lg text-white leading-snug">${film.title}</h3>
            <p class="font-body text-xs text-on-surface-variant line-clamp-2 leading-relaxed">
              ${film.overview || 'Atmospheric film saved to your private collection.'}
            </p>

            <!-- Card Actions -->
            <div class="flex items-center gap-2 pt-2">
              <a href="movie.html?title=${encodeURIComponent(film.title)}" class="flex-1 bg-white text-background font-semibold text-xs py-2 px-3 rounded text-center hover:bg-secondary transition-colors">
                Details
              </a>
              <a href="discover.html?movie=${encodeURIComponent(film.title)}" class="bg-white/10 text-white font-medium text-xs py-2 px-3 rounded hover:bg-white/20 transition-colors flex items-center gap-1" title="Find Similar Movies">
                <span class="material-symbols-outlined text-sm">auto_awesome</span>
              </a>
              <button data-remove-title="${film.title}" class="remove-card-btn bg-red-500/20 text-red-300 hover:bg-red-500/40 p-2 rounded transition-colors" title="Remove from Watchlist">
                <span class="material-symbols-outlined text-sm">delete</span>
              </button>
            </div>
          </div>
        </div>
      `;

      // Attach removal click handler
      const removeBtn = card.querySelector('.remove-card-btn');
      if (removeBtn) {
        removeBtn.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          card.classList.add('card-exit-active');
          setTimeout(() => {
            const currentList = getWatchlist().filter(item => item.title.toLowerCase() !== film.title.toLowerCase());
            saveWatchlist(currentList);
            renderWatchlist();
          }, 350);
        });
      }

      watchlistGrid.appendChild(card);
    });
  }
});
