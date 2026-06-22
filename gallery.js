// Renders gallery tiles for a page from window.GALLERY / window.BOOKS (content.js).
// A page opts in with: <div class="grid" id="gallery" data-section="comics"></div>
(function () {
  var el = document.getElementById('gallery');
  if (!el) return;
  var section = el.getAttribute('data-section');
  var books   = (window.BOOKS && window.BOOKS[section]) || [];
  var singles = (window.GALLERY && window.GALLERY[section]) || [];

  if (!books.length && !singles.length) {
    el.classList.add('gallery-empty');
    el.innerHTML = '<p class="empty-note">No images yet. Drop files into the matching ' +
                   '<code>content/</code> folder, run <code>generate.py</code>, and push.</p>';
    return;
  }

  function imgTile(it) {
    var full  = (typeof it === 'string') ? it : it.full;
    var thumb = (typeof it === 'string') ? it : (it.thumb || it.full);
    var alt = full.split('/').pop().replace(/\.[^.]+$/, '');
    return '<a class="tile" href="' + encodeURI(full) + '" target="_blank" rel="noopener">' +
             '<img src="' + encodeURI(thumb) + '" alt="' + alt + '" loading="lazy">' +
           '</a>';
  }

  function bookTile(b) {
    var cover = b.cover || (b.pages && b.pages[0]);
    var thumb = cover ? (cover.thumb || cover.full) : '';
    var href = 'reader.html?s=' + encodeURIComponent(section) +
               '&c=' + encodeURIComponent(b.slug);
    var count = (b.pages ? b.pages.length : 0) + ' pages';
    return '<a class="tile book" href="' + href + '">' +
             '<img src="' + encodeURI(thumb) + '" alt="' + b.title + '" loading="lazy">' +
             '<span class="book-badge">' + count + '</span>' +
           '</a>';
  }

  // books (multi-page) first, then loose single images
  el.innerHTML = books.map(bookTile).join('') + singles.map(imgTile).join('');
})();
