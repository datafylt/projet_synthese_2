 function previewImages() {
            var previewArea = document.getElementById('imagePreviews');
            previewArea.innerHTML = ''; // Clear existing images

            var files = document.getElementById('fileUpload').files;

            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                var reader = new FileReader();

                reader.onloadend = function(e) {
                    var img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.maxWidth = '500px';
                    img.style.maxHeight = '500px';
                    previewArea.appendChild(img);
                }

                if (file) {
                    reader.readAsDataURL(file);
                }
            }
        }

