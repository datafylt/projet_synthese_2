import os
import shutil
import time

import cv2
import joblib
import yaml
from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import uuid

webapp_root = "webapp"
params_path = "params.yaml"

static_dir = os.path.join(webapp_root, "static")
template_dir = os.path.join(webapp_root, "templates")

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
# Set a secret key for message flashing
app.secret_key = 'your_secret_key'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def predict_input_images(images, web_temp_path):
    predictions = {}
    model = joblib.load("webapp/model_webapp_dir/model.joblib")
    image_shape = (300, 300, 1)  # 300 × 300、graysclaed (full-color : 3)
    for i in range(len(images)):
        img_pred = cv2.imread(web_temp_path + images[i], cv2.IMREAD_GRAYSCALE)
        img_pred = img_pred / 255  # rescale

        # Start the timer
        start_time = time.time()
        prediction = model.predict(img_pred.reshape(1, *image_shape))
        # End the timer
        end_time = time.time()

        # Calculate elapsed time
        elapsed_time = end_time - start_time

        # Predicted Class : defect
        if prediction < 0.5:
            predicted_label = "Defect"
            prob = (1 - prediction.sum()) * 100
        # Predicted Class : OK
        else:
            predicted_label = "Ok"
            prob = prediction.sum() * 100
        predictions[os.path.basename(images[i])] = {"prediction": [predicted_label, str("{:.2f}".format(
            prob)) + "%, process time: " + str("{:.3f}".format(elapsed_time))]}
    return predictions


def saved_predicted_image(save_folder):
    # Ensure the request is JSON
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    # Get the list of images from the request
    image_urls = request.json.get('images', [])
    # Define the folder where you want to save images

    for image_url in image_urls:
        # Extract the filename and create a path to save the image
        filename = os.path.basename(image_url)
        save_path = os.path.join(save_folder, filename)

        # Assume images are coming from a static folder for this example
        static_image_path = os.path.join('', image_url.strip('/').replace('/', os.sep))
        # Copy the file to the new location
        shutil.copy(static_image_path, save_path)


def delete_predicted_image(delete_path):
    data = request.get_json()
    defect_images = data.get('defect_images', [])
    errors = []

    for image_url in defect_images:
        filename = os.path.basename(image_url)
        file_path = os.path.join(delete_path, filename)

        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                errors.append(f"File {filename} not found.")
        except Exception as e:
            errors.append(f"Error deleting file {filename}: {str(e)}")

    if errors:
        return jsonify({"error": "Some images could not be deleted", "details": errors}), 400
@app.route('/', methods=['GET', 'POST'])
def home_page():
    print("going to index")
    return render_template('index.html')


@app.route('/prediction', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("doing prediction")
        # Check if the post request has the file part
        if 'picture' not in request.files:
            flash("No file part", category='error')
            return redirect(request.url)

        uploaded_files = request.files.getlist('picture')
        if len(uploaded_files) == 0:
            flash("No selected file", category='error')
            return redirect(request.url)

        image_predictions = []
        temp_process_path = 'webapp/temp_process/'

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(file.filename.rsplit('.', 1)[0])
                unique_filename = f"{filename}_{uuid.uuid4()}.{ext}"
                tmp_img_path = os.path.join(temp_process_path, unique_filename)
                file.save(tmp_img_path)

                # Perform prediction
                prediction_result = predict_input_images([unique_filename], temp_process_path)
                prediction_label = prediction_result.get(unique_filename).get("prediction")[0]
                prediction_val = prediction_result.get(unique_filename).get("prediction")[1]

                # Prepare the destination path based on the prediction
                sub_folder = "ok_front" if prediction_label == "Ok" else "def_front"
                img_destination_path = os.path.join('webapp/predicted_images', sub_folder, unique_filename)

                # Copy the image to the new destination and delete the temporary one
                shutil.move(tmp_img_path, img_destination_path)

                # Prepare the result message for each image
                image_predictions.append({
                    'filename': filename,
                    'prediction_label': prediction_label,
                    'prediction_val': prediction_val,
                    'image_path': os.path.join(sub_folder, unique_filename)
                    # The path relative to 'webapp/predicted_images'
                })
            else:
                flash(f"File {file.filename} is not an authorized file!", category='error')

        session['image_predictions'] = image_predictions
        return redirect(url_for('results'))
    else:
        print("going to index")
        return render_template('prediction.html')


@app.route('/results')
def results():
    # Retrieve the predictions from the session or an empty list if not present
    image_predictions = session.get('image_predictions', [])
    # Clear the session for image predictions
    session.pop('image_predictions', None)
    return render_template('prediction.html', predictions=image_predictions)



@app.route('/analysis')
def analysis():
    # Define allowed image extensions
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    # Function to check if a file is an image
    def is_image(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    # Gather OK images
    image_folder_ok = os.path.join('webapp', 'predicted_images', 'ok_front')
    image_files_ok = [f for f in os.listdir(image_folder_ok) if is_image(f)]
    image_urls_ok = ['/webapp/predicted_images/ok_front/' + file for file in image_files_ok]

    # Gather Defect images
    image_folder_def = os.path.join('webapp', 'predicted_images', 'def_front')
    image_files_def = [f for f in os.listdir(image_folder_def) if is_image(f)]
    image_urls_def = ['/webapp/predicted_images/def_front/' + file for file in image_files_def]

    # Send both lists of image URLs to the template
    return render_template('analysis.html', image_urls_ok=image_urls_ok, image_urls_def=image_urls_def)


@app.route('/webapp/predicted_images/ok_front/<filename>')
def ok_front_images(filename):
    return send_from_directory('webapp/predicted_images/ok_front', filename)


@app.route('/webapp/predicted_images/def_front/<filename>')
def def_front_images(filename):
    return send_from_directory('webapp/predicted_images/def_front', filename)


@app.route('/save_ok_images', methods=['POST'])
def save_ok_images():
    save_folder = 'webapp/temp_process/for_new_model/ok_front'
    saved_predicted_image(save_folder)
    return jsonify({"success": "OK Images saved"}), 200


@app.route('/save_defect_images', methods=['POST'])
def save_defect_images():
    save_folder = 'webapp/temp_process/for_new_model/ok_front'
    saved_predicted_image(save_folder)
    return jsonify({"success": "Defect Images saved"}), 200


@app.route('/delete_defect_images', methods=['POST'])
def delete_defect_images():
    del_def_path = 'webapp/predicted_images/def_front'
    delete_predicted_image(del_def_path)
    return jsonify({"success": "Selected defect images deleted"}), 200


@app.route('/delete_ok_images', methods=['POST'])
def delete_ok_images():
    del_ok_path = 'webapp/predicted_images/ok_front'
    delete_predicted_image(del_ok_path)
    return jsonify({"success": "Selected defect images deleted"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

