(function initKnightGroupGoogleReviews() {
    var track = document.getElementById('kg-review-track');
    var dotsWrap = document.getElementById('kg-review-dots');
    var prev = document.getElementById('kg-review-prev');
    var next = document.getElementById('kg-review-next');
    var summaryEl = document.getElementById('kg-review-summary');

    if (!track || !dotsWrap || !prev || !next) {
        return;
    }

    var AVATAR_COLORS = ['#1a56c4', '#c0392b', '#1e6b2e', '#FBBC05', '#7c3aed', '#0f766e'];

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function initial(name) {
        var clean = String(name || '').trim();
        return clean ? clean.charAt(0).toUpperCase() : '?';
    }

    function stars(count) {
        var n = Math.max(1, Math.min(5, Number(count) || 5));
        var out = '';
        for (var i = 0; i < n; i += 1) {
            out += '\u2605';
        }
        return out;
    }

    function avatarColor(name, index) {
        if (name) {
            var sum = 0;
            for (var i = 0; i < name.length; i += 1) {
                sum += name.charCodeAt(i);
            }
            return AVATAR_COLORS[sum % AVATAR_COLORS.length];
        }
        return AVATAR_COLORS[index % AVATAR_COLORS.length];
    }

    function cardMarkup(review, index) {
        var name = review.name || 'Google User';
        var meta = review.meta || 'Google review';
        var bg = review.avatarColor || avatarColor(name, index);
        var starLabel = String(Number(review.stars) || 5) + ' stars';
        var textStyle = bg === '#FBBC05' ? ' style="color:#1d1c1f;"' : '';

        return (
            '<article class="kg-review-card">' +
            '<div class="kg-review-header">' +
            '<span class="kg-review-avatar" style="background:' + escapeHtml(bg) + ';"' + textStyle + ' aria-hidden="true">' + escapeHtml(initial(name)) + '</span>' +
            '<div><h3 class="kg-review-name">' + escapeHtml(name) + '</h3>' +
            '<div class="kg-review-sub">' + escapeHtml(meta) + '</div></div></div>' +
            '<div class="kg-stars" role="img" aria-label="' + escapeHtml(starLabel) + '">' + stars(review.stars) + '</div>' +
            '<p class="kg-review-text">' + escapeHtml(review.text || '') + '</p>' +
            '<div class="kg-review-date">' + escapeHtml(review.date || '') + '</div>' +
            '</article>'
        );
    }

    function applySummary(payload) {
        if (!summaryEl || !payload) {
            return;
        }
        var rating = Number(payload.ratingValue || 5).toFixed(1);
        var count = Number(payload.reviewCount || 0);
        if (!count && track.children.length) {
            count = track.children.length;
        }
        summaryEl.textContent = rating + ' \u00b7 ' + count + ' reviews';
        var mapRating = document.querySelector('.kg-map-rating');
        if (mapRating) {
            mapRating.textContent = '\u2605\u2605\u2605\u2605\u2605 ' + rating + ' \u00b7 ' + count + ' Google reviews';
            mapRating.setAttribute('aria-label', rating + ' out of 5 stars, ' + count + ' Google reviews');
        }
    }

    function startCarousel() {
        var cards = Array.prototype.slice.call(track.children);
        var index = 0;

        function perView() {
            if (window.innerWidth < 760) {
                return 1;
            }
            if (window.innerWidth < 1100) {
                return 2;
            }
            return 3;
        }

        function pageCount() {
            return Math.max(1, Math.ceil(cards.length / perView()));
        }

        function renderDots() {
            dotsWrap.innerHTML = '';
            for (var i = 0; i < pageCount(); i += 1) {
                var dot = document.createElement('button');
                dot.type = 'button';
                dot.className = 'kg-review-dot' + (i === index ? ' is-active' : '');
                dot.setAttribute('aria-label', 'Go to review set ' + (i + 1));
                (function (target) {
                    dot.addEventListener('click', function () {
                        index = target;
                        update();
                    });
                })(i);
                dotsWrap.appendChild(dot);
            }
        }

        function update() {
            var pages = pageCount();
            if (index > pages - 1) {
                index = pages - 1;
            }
            if (index < 0) {
                index = 0;
            }
            var sample = cards[0];
            var gap = 24;
            var width = sample ? sample.getBoundingClientRect().width : 0;
            var offset = index * (width + gap) * perView();
            track.style.transform = 'translateX(' + (-offset) + 'px)';
            Array.prototype.forEach.call(dotsWrap.children, function (dot, dotIndex) {
                dot.classList.toggle('is-active', dotIndex === index);
            });
            prev.disabled = index === 0;
            next.disabled = index === pages - 1;
        }

        prev.addEventListener('click', function () {
            index -= 1;
            update();
        });
        next.addEventListener('click', function () {
            index += 1;
            update();
        });
        window.addEventListener('resize', function () {
            renderDots();
            update();
        });

        renderDots();
        update();
    }

    function loadFeed() {
        return fetch('./data/google-reviews.json?v=20260603', { cache: 'no-store' })
            .then(function (response) {
                if (!response.ok) {
                    return null;
                }
                return response.json();
            })
            .catch(function () {
                return null;
            });
    }

    loadFeed().then(function (payload) {
        if (payload && Array.isArray(payload.reviews) && payload.reviews.length) {
            track.innerHTML = payload.reviews.map(cardMarkup).join('');
            applySummary(payload);
        } else {
            applySummary({ ratingValue: 5, reviewCount: track.children.length });
        }
        startCarousel();
    });
})();
