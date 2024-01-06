import os
import shutil
import time

import cv2
import joblib
import yaml
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import uuid

webapp_root = "webapp"
params_path = "params.yaml"

static_dir = os.path.join(webapp_root, "static")
template_dir = os.path.join(webapp_root, "templates")

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

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
        if (prediction < 0.5):
            predicted_label = "Defect"
            prob = (1 - prediction.sum()) * 100
        # Predicted Class : OK
        else:
            predicted_label = "Ok"
            prob = prediction.sum() * 100
        predictions[os.path.basename(images[i])] = {"prediction": [predicted_label, str("{:.2f}".format(prob)) + "%, process time: " +  str("{:.3f}".format(elapsed_time))]}
    return predictions


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'picture' not in request.files:
            return render_template("index.html", response="No file part")

        uploaded_files = request.files.getlist('picture')
        if len(uploaded_files) == 0:
            return render_template("index.html", response="No selected file")
        images = []
        auth_prediction = {}
        temp_process_path = 'webapp/temp_process/'
        map_unique_name = {}
        for file in uploaded_files:
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{ext}"
            filename = secure_filename(file.filename)
            map_unique_name[unique_filename] = filename
            if file and allowed_file(file.filename):
                tmp_img_path = os.path.join(temp_process_path, unique_filename)
                file.save(tmp_img_path)
                images.append(unique_filename)
                auth_prediction[unique_filename] = True
            elif file and not allowed_file(file.filename):
                auth_prediction[unique_filename] = False

        result = predict_input_images(images, temp_process_path)
        # Delete file after prediction
        # os.remove(tmp_img_path)
        response_msg = ''
        predicted_path = 'webapp/predicted_images/'
        for unique_fname in auth_prediction:
            if auth_prediction[unique_fname]:
                real_fname = map_unique_name[unique_fname]
                prediction_label = result.get(unique_fname).get("prediction")[0]
                prediction_val = result.get(unique_fname).get("prediction")[1]
                msg =''
                tmp_img_source_path = temp_process_path + unique_fname
                if prediction_label == "Ok":
                    img_destination_path = predicted_path + "ok_front/" + real_fname + "_" + unique_fname
                    msg += ("The part file " + real_fname +
                            " is consider OK at " + prediction_val)
                else:
                    img_destination_path = predicted_path + "def_front/" + real_fname + "_" + unique_fname
                    msg += ("The part file (" + real_fname +
                            ") is consider Defect at " + prediction_val)

                shutil.copy(tmp_img_source_path, img_destination_path)
                # Delete file from temp process file after prediction
                os.remove(temp_process_path + unique_fname)
                response_msg += (msg +"\n")
            else:
                response_msg +=  real_fname + " - This file is not an authorized file!"

        return render_template("index.html", response=response_msg)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
