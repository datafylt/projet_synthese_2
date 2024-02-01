// Declare items array in the global scope
var items = [];
var pswpElement = document.querySelector('.pswp');
document.addEventListener("DOMContentLoaded", function () {


    if (!pswpElement) {
        console.error('PhotoSwipe element not found in the DOM.');
        return;
    }

    // Call this function initially and after adding new images
    initializePhotoSwipeEventListeners();
});

function initializePhotoSwipeEventListeners() {
    var links = document.querySelectorAll('.my-gallery a');
    links.forEach(function (link, index) {
        link.removeEventListener('click', handleGalleryClick); // Remove existing event listener to avoid duplicates
        link.addEventListener('click', handleGalleryClick);
    });
}

function handleGalleryClick(event) {
    event.preventDefault();
    var clickedItemSrc = event.currentTarget.getAttribute('data-pswp-src');
    var index = items.findIndex(item => item.src === clickedItemSrc);
    if (index !== -1) {
        openPhotoSwipe(index);
    } else {
        console.error('Clicked item not found in items array');
    }
}

function previewImages() {
    var previewArea = document.getElementById('imagePreviews');
    previewArea.innerHTML = ''; // Clear existing images
    items.length = 0; // Clear existing items

    var files = document.getElementById('fileUpload').files;

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file.type.startsWith('image/')) {
            var reader = new FileReader();

            reader.onloadend = function(e) {
                var base64ImageSrc = e.target.result;
                var img = document.createElement('img');
                img.src = base64ImageSrc;
                img.classList.add('img-thumbnail');
                img.style.maxWidth = '200px';
                img.style.height = 'auto';

                var anchor = document.createElement('a');
                anchor.href = '#';
                anchor.setAttribute('data-pswp-src', base64ImageSrc);
                anchor.setAttribute('data-size', '1200x800');
                anchor.appendChild(img);

                previewArea.appendChild(anchor);

                items.push({
                    src: base64ImageSrc,
                    w: 1200,
                    h: 800
                });

                // Initialize event listeners after each image is added
                initializePhotoSwipeEventListeners();
            };

            reader.readAsDataURL(file);
        }
    }
}


function openPhotoSwipe(index) {
    var options = {
        index: index,
        bgOpacity: 0.7,
        showHideOpacity: true,
        maxSpreadZoom: 3, // Increase this value to allow zooming beyond 100%
        getDoubleTapZoom: function (isMouseClick, item) {
            if (isMouseClick) {
                return 1.5; // Allow the mouse click to zoom to 100%
            } else {
                return item.initialZoomLevel < 0.7 ? 3 : 1; // On double-tap, zoom to the maximum available image resolution
            }
        }
    };
    var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
    gallery.init();
}