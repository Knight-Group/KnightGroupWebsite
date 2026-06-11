(function () {
    var state = {
        groups: [],
        lightbox: {
            groupIndex: 0,
            imageIndex: 0
        }
    };

    function categoryLabel(id, categories) {
        var match = (categories || []).find(function (item) {
            return item.id === id;
        });
        return match ? match.label : 'Project';
    }

    function encodeSrc(src) {
        return src.split('/').map(function (part, index) {
            return index === 0 ? part : encodeURIComponent(part);
        }).join('/');
    }

    function openLightbox(groupIndex, imageIndex) {
        var lightbox = document.getElementById('gallery-lightbox');
        if (!lightbox || !state.groups[groupIndex]) return;

        state.lightbox.groupIndex = groupIndex;
        state.lightbox.imageIndex = imageIndex;
        renderLightbox();
        lightbox.classList.add('is-open');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        var lightbox = document.getElementById('gallery-lightbox');
        if (!lightbox) return;
        lightbox.classList.remove('is-open');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    function shiftLightbox(delta) {
        var group = state.groups[state.lightbox.groupIndex];
        if (!group) return;

        var nextIndex = state.lightbox.imageIndex + delta;
        if (nextIndex < 0 || nextIndex >= group.images.length) return;
        state.lightbox.imageIndex = nextIndex;
        renderLightbox();
    }

    function renderLightbox() {
        var group = state.groups[state.lightbox.groupIndex];
        if (!group) return;

        var image = group.images[state.lightbox.imageIndex];
        var img = document.getElementById('gallery-lightbox-img');
        var eyebrow = document.getElementById('gallery-lightbox-eyebrow');
        var title = document.getElementById('gallery-lightbox-title');
        var text = document.getElementById('gallery-lightbox-text');
        var prev = document.getElementById('gallery-lightbox-prev');
        var next = document.getElementById('gallery-lightbox-next');

        if (img) {
            img.src = encodeSrc(image.src);
            img.alt = image.seoAlt || image.title;
        }
        if (eyebrow) {
            if (image.beforeAfter) {
                eyebrow.textContent = 'Before & After';
            } else if (group.progression && group.images.length > 1) {
                eyebrow.textContent = 'Stage ' + image.step + ' of ' + group.images.length;
            } else {
                eyebrow.textContent = group.title;
            }
        }
        if (title) title.textContent = image.title;
        if (text) text.textContent = image.description;

        if (prev) prev.disabled = state.lightbox.imageIndex === 0;
        if (next) next.disabled = state.lightbox.imageIndex >= group.images.length - 1;
    }

    function createShot(groupIndex, image, group) {
        var shot = document.createElement('button');
        shot.type = 'button';
        shot.className = 'gallery-shot';
        shot.setAttribute('aria-label', 'Open image: ' + image.title);

        var media = document.createElement('div');
        media.className = 'gallery-shot__media';

        var img = document.createElement('img');
        img.src = encodeSrc(image.src);
        img.alt = image.seoAlt || image.title;
        img.loading = 'lazy';
        img.decoding = 'async';
        media.appendChild(img);

        if (image.beforeAfter) {
            var badge = document.createElement('span');
            badge.className = 'gallery-shot__badge';
            badge.textContent = 'Before & After';
            media.appendChild(badge);
        } else if (group.progression && group.images.length > 1) {
            var step = document.createElement('span');
            step.className = 'gallery-shot__step';
            step.textContent = 'Stage ' + image.step;
            media.appendChild(step);
        }

        var body = document.createElement('div');
        body.className = 'gallery-shot__body';

        var shotTitle = document.createElement('p');
        shotTitle.className = 'gallery-shot__title';
        shotTitle.textContent = image.title;

        var shotText = document.createElement('p');
        shotText.className = 'gallery-shot__text';
        shotText.textContent = image.description;

        body.appendChild(shotTitle);
        body.appendChild(shotText);
        shot.appendChild(media);
        shot.appendChild(body);

        shot.addEventListener('click', function () {
            openLightbox(groupIndex, group.images.indexOf(image));
        });

        return shot;
    }

    function createProjectCard(group, groupIndex, categories) {
        var card = document.createElement('article');
        card.className = 'gallery-project';
        card.id = 'project-' + group.id;
        card.dataset.category = group.category;

        if (group.beforeAfter) card.classList.add('gallery-project--before-after');
        if (group.progression) card.classList.add('gallery-project--progression');

        var head = document.createElement('div');
        head.className = 'gallery-project__head';

        var copy = document.createElement('div');
        copy.className = 'gallery-project__copy';

        var eyebrow = document.createElement('span');
        eyebrow.className = 'gallery-project__eyebrow';
        if (group.beforeAfter) {
            eyebrow.textContent = 'Before & After';
        } else if (group.progression) {
            eyebrow.textContent = group.images.length + '-stage project';
        } else {
            eyebrow.textContent = categoryLabel(group.category, categories);
        }

        var title = document.createElement('h3');
        title.className = 'gallery-project__title';
        title.textContent = group.title;

        var text = document.createElement('p');
        text.className = 'gallery-project__text';
        text.textContent = group.description;

        copy.appendChild(eyebrow);
        copy.appendChild(title);
        copy.appendChild(text);

        var link = document.createElement('a');
        link.className = 'gallery-project__link';
        link.href = group.serviceLink;
        link.textContent = 'Related service';

        head.appendChild(copy);
        head.appendChild(link);

        var shots = document.createElement('div');
        shots.className = 'gallery-project__shots';
        group.images.forEach(function (image) {
            shots.appendChild(createShot(groupIndex, image, group));
        });

        card.appendChild(head);
        card.appendChild(shots);
        return card;
    }

    function renderProjects(groups, categories, activeFilter) {
        var mount = document.getElementById('gallery-projects');
        if (!mount) return;

        mount.innerHTML = '';
        var visible = groups.filter(function (group) {
            return activeFilter === 'all' || group.category === activeFilter;
        });

        if (!visible.length) {
            mount.innerHTML = '<p class="gallery-projects__empty">No projects match this filter yet. Choose another category or view all projects.</p>';
            return;
        }

        visible.forEach(function (group) {
            var groupIndex = groups.indexOf(group);
            mount.appendChild(createProjectCard(group, groupIndex, categories));
        });
    }

    function renderFilters(categories, activeFilter, onChange) {
        var mount = document.getElementById('gallery-filters');
        if (!mount) return;

        mount.innerHTML = '';
        categories.forEach(function (category) {
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'gallery-filter' + (category.id === activeFilter ? ' is-active' : '');
            button.textContent = category.label;
            button.dataset.filter = category.id;
            button.addEventListener('click', function () {
                onChange(category.id);
            });
            mount.appendChild(button);
        });
    }

    function bindLightbox() {
        var lightbox = document.getElementById('gallery-lightbox');
        var closeBtn = document.getElementById('gallery-lightbox-close');
        var prevBtn = document.getElementById('gallery-lightbox-prev');
        var nextBtn = document.getElementById('gallery-lightbox-next');
        var dialog = document.querySelector('.gallery-lightbox__dialog');

        if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
        if (prevBtn) prevBtn.addEventListener('click', function () { shiftLightbox(-1); });
        if (nextBtn) nextBtn.addEventListener('click', function () { shiftLightbox(1); });

        if (lightbox) {
            lightbox.addEventListener('click', function (event) {
                if (event.target === lightbox) closeLightbox();
            });
        }

        if (dialog) {
            dialog.addEventListener('click', function (event) {
                event.stopPropagation();
            });
        }

        document.addEventListener('keydown', function (event) {
            var isOpen = lightbox && lightbox.classList.contains('is-open');
            if (!isOpen) return;
            if (event.key === 'Escape') closeLightbox();
            if (event.key === 'ArrowLeft') shiftLightbox(-1);
            if (event.key === 'ArrowRight') shiftLightbox(1);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        bindLightbox();

        fetch('GalleryImages/gallery-manifest.json')
            .then(function (response) {
                if (!response.ok) throw new Error('manifest load failed');
                return response.json();
            })
            .then(function (data) {
                var categories = data.categories || [{ id: 'all', label: 'All projects' }];
                state.groups = data.groups || [];
                var activeFilter = 'all';

                function setFilter(nextFilter) {
                    activeFilter = nextFilter;
                    renderFilters(categories, activeFilter, setFilter);
                    renderProjects(state.groups, categories, activeFilter);
                }

                setFilter(activeFilter);
            })
            .catch(function () {
                var mount = document.getElementById('gallery-projects');
                if (mount) {
                    mount.innerHTML = '<p class="gallery-projects__error">Gallery images could not be loaded. Please refresh or contact us for project photos.</p>';
                }
            });
    });
})();
