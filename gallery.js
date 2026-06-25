// Renders gallery tiles from window.GALLERY / window.BOOKS / window.GROUPS (content.js).
// A page opts in with: <div class="grid" id="gallery" data-section="comics"></div>
(function () {
  var el = document.getElementById('gallery');
  if (!el) return;
  var section = el.getAttribute('data-section');
  var books    = (window.BOOKS  && window.BOOKS[section])  || [];
  var singles  = (window.GALLERY && window.GALLERY[section]) || [];
  var projects = (window.GROUPS && window.GROUPS[section]) || [];

  if (!books.length && !singles.length && !projects.length) {
    el.classList.add('gallery-empty');
    el.innerHTML = '<p class="empty-note">No images yet. Drop files into the matching ' +
                   '<code>content/</code> folder, run <code>generate.py</code>, and push.</p>';
    return;
  }

  // comics use the spread reader; everything else uses the illustration reader
  var illReader = 'illreader.html';
  var singlesReader = (section === 'comics') ? 'reader.html' : illReader;
  // TEMP TEST: route comic books to the new PhotoSwipe reader so clicking a cover
  // opens it. Revert bookReader to 'reader.html' when done testing.
  var bookReader = (section === 'comics') ? 'comics-photoswipe.html' : 'reader.html';

  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function tn(it){ return encodeURI((typeof it === 'string') ? it : (it.thumb || it.full)); }
  function altOf(it){ var f=(typeof it==='string')?it:it.full; return f.split('/').pop().replace(/\.[^.]+$/,''); }

  function bookTile(b){
    var cover = b.cover || (b.pages && b.pages[0]);
    var href = bookReader + '?s=' + encodeURIComponent(section) + '&c=' + encodeURIComponent(b.slug);
    return '<a class="tile book" href="' + href + '"><img src="' + tn(cover) +
           '" alt="' + esc(b.title) + '" loading="lazy"></a>';
  }
  // a project shows ONLY its hero (a) in the grid; opens the whole set in the reader
  function groupTile(g){
    var href = illReader + '?s=' + encodeURIComponent(section) + '&g=' + encodeURIComponent(g.base);
    return '<a class="tile" href="' + href + '"><img src="' + tn(g.images[0]) +
           '" alt="' + esc(g.base) + '" loading="lazy"></a>';
  }
  function imgTile(it, idx){
    var href = singlesReader + '?s=' + encodeURIComponent(section) + '&i=' + idx;
    return '<a class="tile" href="' + href + '"><img src="' + tn(it) +
           '" alt="' + altOf(it) + '" loading="lazy"></a>';
  }

  // books, then project covers, then loose single images
  el.innerHTML = books.map(bookTile).join('') +
                 projects.map(groupTile).join('') +
                 singles.map(function (it, idx) { return imgTile(it, idx); }).join('');
})();
