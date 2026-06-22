// Shared nav behavior across all pages
(function () {
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  var links = document.getElementById('navlinks');
  if (links) {
    // Highlight the current page in the nav
    var here = location.pathname.split('/').pop() || 'index.html';
    links.querySelectorAll('a').forEach(function (a) {
      if (a.getAttribute('href') === here) a.classList.add('active');
      a.addEventListener('click', function () { links.classList.remove('open'); });
    });
  }
})();
