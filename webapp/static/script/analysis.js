document.addEventListener("DOMContentLoaded", function () {
    var pswpElement = document.querySelector('.pswp');

    if (!pswpElement) {
        console.error('PhotoSwipe element not found in the DOM.');
        return;
    }

    var items = [];
    var links = document.querySelectorAll('.my-gallery a');
    links.forEach(function (link, index) {
        var size = link.getAttribute('data-size').split('x');
        if (size.length === 2) {
            items.push({
                src: link.getAttribute('href'),
                w: parseInt(size[0], 10),
                h: parseInt(size[1], 10)
            });
        } else {
            console.error('Invalid data-size attribute for:', link.getAttribute('href'));
        }
    });

    links.forEach(function (link, index) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            openPhotoSwipe(index);
        });
    });

    function openPhotoSwipe(index) {
        var options = {
            index: index,
            bgOpacity: 0.7,
            showHideOpacity: true,
            maxSpreadZoom: 3, // Increase this value to allow zooming beyond 100%
            getDoubleTapZoom: function (isMouseClick, item) {
                if (isMouseClick) {
                    // Allow the mouse click to zoom to 100%
                    return 1.5;
                } else {
                    // On double-tap, zoom to the maximum available image resolution
                    return item.initialZoomLevel < 0.7 ? 3 : 1;
                }
            }
        };

        var gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
        gallery.init();
    }

    // Prevent checkbox clicks from triggering PhotoSwipe
    document.querySelectorAll('.image-checkbox').forEach(function (checkbox) {
        checkbox.addEventListener('click', function (event) {
            event.stopPropagation();
        });
    });


    var okDeleteButton = document.getElementById('okImageForm').querySelector('.btn-danger');
    var confirmationModal = $('#confirmationModal');

    if (okDeleteButton) {
        okDeleteButton.addEventListener('click', function (event) {
            event.preventDefault();
            // Show the confirmation modal
            confirmationModal.modal('show');
        });
    }

    var defectDeleteButton = document.getElementById('defectImageForm').querySelector('.btn-danger');

    if (defectDeleteButton) {
        defectDeleteButton.addEventListener('click', function (event) {
            event.preventDefault();
            // Show the confirmation modal
            confirmationModal.modal('show');
        });
    }

    var confirmDeletionButton = document.getElementById('confirmDeletion');
    var selectedImagesType; // Variable to store the type of images to delete

    if (okDeleteButton) {
        okDeleteButton.addEventListener('click', function (event) {
            event.preventDefault();
            selectedImagesType = 'ok_images'; // Set the type of images to delete
            confirmationModal.modal('show');
        });
    }

    if (defectDeleteButton) {
        defectDeleteButton.addEventListener('click', function (event) {
            event.preventDefault();
            selectedImagesType = 'defect_images'; // Set the type of images to delete
            confirmationModal.modal('show');
        });
    }

    if (confirmDeletionButton) {
        confirmDeletionButton.addEventListener('click', function () {
            confirmationModal.modal('hide'); // Hide the modal immediately on confirmation

            // Depending on the selected type, call the delete function
            if (selectedImagesType === 'ok_images') {
                deleteImages('ok_images', '/delete_ok_images');
            } else if (selectedImagesType === 'defect_images') {
                deleteImages('defect_images', '/delete_defect_images');
            }
        });
    }


});

// Handle OK Image Form Submission
document.getElementById('okImageForm').addEventListener('submit', function (event) {
    event.preventDefault();
    submitSelectedImages('ok_images', '/save_ok_images');
});

// Handle Defect Image Form Submission
document.getElementById('defectImageForm').addEventListener('submit', function (event) {
    event.preventDefault();
    submitSelectedImages('defect_images', '/save_defect_images');
});

function submitSelectedImages(imageType, url) {
    var selectedImages = Array.from(document.querySelectorAll(`input[name="${imageType}"]:checked`))
        .map(checkbox => checkbox.value);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({images: selectedImages})
    })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Handle the response from the server
        });
}

function deleteImages(imageType, endpoint) {
    var selectedImages = Array.from(document.querySelectorAll(`input[name="${imageType}"]:checked`))
        .map(function (checkbox) {
            return checkbox.value;
        });

    var alertModal = $('#alertModal');
    var alertModalBody = document.getElementById('alertModalBody');

    if (selectedImages.length === 0) {
        alertModalBody.textContent = 'Please select at least one image to delete.';
        alertModal.modal('show');
        return;
    }

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Include CSRF token as necessary
        },
        body: JSON.stringify({[imageType]: selectedImages})
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            console.log(data); // Handle success
             $('#confirmationModal').modal('hide');
             window.location.reload();
        })
        .catch(function (error) {
            console.error(error); // Handle errors
            $('#confirmationModal').modal('hide');
        });
}