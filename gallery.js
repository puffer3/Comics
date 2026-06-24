// Renders gallery tiles for a page from window.GALLERY / window.BOOKS (content.js).
// A page opts in with: <div class="grid" id="gallery" data-section="comics"></div>
(function () {
  var el = document.getElementById('gallery');
  if (!el) return;
  var section = el.getAttribute('data-section');
  var books   = (window.BOOKS && window.BOOKS[section]) || [];
  var singles = (window.GALLERY && window.GALLERY[section]) || [];
  var projects = (window.GROUPS && window.GROUPS[section]) || [];

  if (!books.length && !singles.length && !projects.length) {
    el.classList.add('gallery-empty');
    el.innerHTML = '<p class="empty-note">No images yet. Drop files into the matching ' +
                   '<code>content/</code> folder, run <code>generate.py</code>, and push.</p>';
    return;
  }

  function imgTile(it, idx) {
    var full  = (typeof it === 'string') ? it : it.full;
    var thumb = (typeof it === 'string') ? it : (it.thumb || it.full);
    var alt = full.split('/').pop().replace(/\.[^.]+$/, '');
    // open in the viewer (arrow keys / tap), starting at this image
    var href = 'reader.html?s=' + encodeURIComponent(section) + '&i=' + idx;
    return '<a class="tile" data-i="' + idx + '" href="' + href + '">' +
             '<img src="' + encodeURI(thumb) + '" alt="' + alt + '" loading="lazy">' +
           '</a>';
  }

  function bookTile(b) {
    var cover = b.cover || (b.pages && b.pages[0]);
    var thumb = cover ? (cover.thumb || cover.full) : '';
    var href = 'reader.html?s=' + encodeURIComponent(section) +
               '&c=' + encodeURIComponent(b.slug);
    return '<a class="tile book" href="' + href + '">' +
             '<img src="' + encodeURI(thumb) + '" alt="' + b.title + '" loading="lazy">' +
           '</a>';
  }

  function tn(it) { return encodeURI(it.thumb || it.full); }

  // a "project": hero (a) big on the left, the rest stacked small on the right
  function projectBlock(g) {
    var base = encodeURIComponent(g.base);
    var hero = g.images[0];
    var rest = g.images.slice(1);
    var col = rest.map(function (it, ri) {
      return '<a class="proj-thumb" href="reader.html?s=' + encodeURIComponent(section) +
             '&g=' + base + '&i=' + (ri + 1) + '"><img src="' + tn(it) + '" loading="lazy"></a>';
    }).join('');
    return '<div class="project">' +
             '<a class="proj-hero" href="reader.html?s=' + encodeURIComponent(section) +
               '&g=' + base + '&i=0"><img src="' + tn(hero) + '" loading="lazy"></a>' +
             '<div class="proj-col">' + col + '</div>' +
           '</div>';
  }

  // projects render as block rows ABOVE the square grid
  if (projects.length) {
    el.insertAdjacentHTML('beforebegin',
      '<div class="project-groups">' + projects.map(projectBlock).join('') + '</div>');
  }

  // books (multi-page) first, then loose single images
  el.innerHTML = books.map(bookTile).join('') +
                 singles.map(function (it, idx) { return imgTile(it, idx); }).join('');
})();
