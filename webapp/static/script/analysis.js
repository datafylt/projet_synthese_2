document.addEventListener("DOMContentLoaded", function () {
    // PhotoSwipe Initialization
    var pswpElement = document.querySelector('.pswp');

    if (!pswpElement) {
        console.error('PhotoSwipe element not found in the DOM.');
        return;
    }

    var items = [];
    var links = document.querySelectorAll('.my-gallery a');
    links.forEach(function (link) {
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
            showHideOpacity: true
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

    // Setup Delete Button and Confirmation Modal Logic
    setupDeleteButtonAndModal();

    // Handle OK Image Form Submission
    document.getElementById('okImageForm').addEventListener('submit', function (event) {
        event.preventDefault();
        submitForm('/save_ok_images', this);
    });

    // Handle Defect Image Form Submission
    document.getElementById('defectImageForm').addEventListener('submit', function (event) {
        event.preventDefault();
        submitForm('/save_defect_images', this);
    });

    function submitForm(url, formElement) {
        var formData = new FormData(formElement);

        fetch(url, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // Refresh the page
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function setupDeleteButtonAndModal() {
        var okDeleteButton = document.getElementById('okImageForm').querySelector('.btn-danger');
        var defectDeleteButton = document.getElementById('defectImageForm').querySelector('.btn-danger');
        var confirmationModal = $('#confirmationModal');
        var confirmDeletionButton = document.getElementById('confirmDeletion');
        var selectedImagesType;

        function setupDeleteButton(deleteButton, imageType) {
            if (deleteButton) {
                deleteButton.addEventListener('click', function (event) {
                    event.preventDefault();
                    selectedImagesType = imageType;
                    confirmationModal.modal('show');
                });
            }
        }

        setupDeleteButton(okDeleteButton, 'ok_images');
        setupDeleteButton(defectDeleteButton, 'defect_images');

        if (confirmDeletionButton) {
            confirmDeletionButton.addEventListener('click', function () {
                confirmationModal.modal('hide');
                if (selectedImagesType === 'ok_images') {
                    deleteImages('ok_images', '/delete_ok_images');
                } else if (selectedImagesType === 'defect_images') {
                    deleteImages('defect_images', '/delete_defect_images');
                }
            });
        }
    }

    function deleteImages(imageType, endpoint) {
        var selectedImages = Array.from(document.querySelectorAll(`input[name="${imageType}"]:checked`))
            .map(checkbox => checkbox.value);

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
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({[imageType]: selectedImages})
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // Refresh the page
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                alertModal.modal('hide');
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