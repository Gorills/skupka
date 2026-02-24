(function() {
    var STORAGE_KEY = 'cookie_consent_accepted';
    var banner = document.getElementById('cookie-banner');
    var acceptBtn = document.getElementById('cookie-banner-accept');

    if (!banner) return;

    function hideBanner() {
        banner.setAttribute('aria-hidden', 'true');
        banner.classList.remove('is-visible');
        try {
            localStorage.setItem(STORAGE_KEY, 'true');
        } catch (e) {}
    }

    function showBanner() {
        banner.setAttribute('aria-hidden', 'false');
        banner.classList.add('is-visible');
    }

    try {
        if (localStorage.getItem(STORAGE_KEY) === 'true') {
            return;
        }
    } catch (e) {}

    showBanner();

    if (acceptBtn) {
        acceptBtn.addEventListener('click', function() {
            hideBanner();
        });
    }
})();
