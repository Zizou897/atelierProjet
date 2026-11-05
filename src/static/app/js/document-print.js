(function () {
  const page = document.querySelector('.page');
  if (!page) return;

  function fitToOnePage() {
    page.style.zoom = '1';
    // Force print CSS/layout to settle before measuring the complete document.
    const contentHeight = page.scrollHeight;
    const printableHeight = (297 - 12) * (96 / 25.4);
    const safetyHeight = printableHeight * 0.97;
    if (contentHeight > safetyHeight) {
      page.style.zoom = (safetyHeight / contentHeight).toFixed(4);
    }
  }

  window.addEventListener('beforeprint', fitToOnePage);
  window.addEventListener('afterprint', function () {
    page.style.zoom = '';
  });
})();
