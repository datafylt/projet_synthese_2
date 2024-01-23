import argparse
import os
import warnings
from urllib.parse import urlparse

import joblib
import mlflow
import yaml
from sklearn.metrics import f1_score, recall_score, accuracy_score, precision_score

warnings.filterwarnings('ignore')

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dropout, Flatten, Dense, Conv2D, MaxPooling2D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras import backend


def generate_model(train_set, test_set, image_shape):
    print(train_set.class_indices)

    backend.clear_session()
    model = Sequential()
    model.add(
        Conv2D(filters=16, kernel_size=(7, 7), strides=2, input_shape=image_shape, activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2))
    model.add(
        Conv2D(filters=32, kernel_size=(3, 3), strides=1, input_shape=image_shape, activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2))
    model.add(
        Conv2D(filters=64, kernel_size=(3, 3), strides=1, input_shape=image_shape, activation='relu', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=2))
    model.add(Flatten())
    model.add(Dense(units=224, activation='relu'))
    model.add(Dropout(rate=0.2))
    model.add(Dense(units=1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    model.summary()

    model_save_path = 'casting_product_detection.hdf5'
    early_stop = EarlyStopping(monitor='val_loss', patience=2)
    checkpoint = ModelCheckpoint(filepath=model_save_path, verbose=1, save_best_only=True, monitor='val_loss')

    n_epochs = 20
    results = model.fit_generator(train_set, epochs=n_epochs, validation_data=test_set,
                                  callbacks=[early_stop, checkpoint])

    return model


def read_params(config_path):
    """
    read parameters from the params.yaml file
    input: params.yaml location
    output: parameters as dictionary
    """
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def accuracymeasures(y_true, y_pred, avg_method):
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average=avg_method)
    recall = recall_score(y_true, y_pred, average=avg_method)
    f1score = f1_score(y_true, y_pred, average=avg_method)
    print("Accuracy Measures")
    print("---------------------", "\n")
    print("Accuracy: ", accuracy)
    print("Precision: ", precision)
    print("Recall: ", recall)
    print("F1 Score: ", f1score)

    return accuracy, precision, recall, f1score


def get_feat_and_target(df, target):
    """
    Get features and target variables seperately from given dataframe and target 
    input: dataframe and target column
    output: two dataframes for x and y 
    """
    x = df.drop(target, axis=1)
    y = df[[target]]
    return x, y


def train_and_evaluate(config_path):
    config = read_params(config_path)
    model_dir = config["model_dir"]
    web_model_dir = config["model_webapp_dir"]

    train_data_path = config["processed_data_config"]["train_casting_data"]
    test_data_path = config["processed_data_config"]["test_casting_data"]
    image_gen = ImageDataGenerator(rescale=1 / 255, zoom_range=0.1, brightness_range=[0.9, 1.0])
    image_shape = (300, 300, 1)  # 300 × 300、graysclaed (full-color : 3)
    batch_size = 32
    train_set = image_gen.flow_from_directory(train_data_path,
                                              target_size=image_shape[:2],
                                              color_mode="grayscale",
                                              classes={'def_front': 0, 'ok_front': 1},
                                              batch_size=batch_size,
                                              class_mode='binary',
                                              shuffle=True,
                                              seed=0)

    test_set = image_gen.flow_from_directory(test_data_path,
                                             target_size=image_shape[:2],
                                             color_mode="grayscale",
                                             classes={'def_front': 0, 'ok_front': 1},
                                             batch_size=batch_size,
                                             class_mode='binary',
                                             shuffle=False,
                                             seed=0)

    target = config["raw_data_config"]["target"]

    ################### MLFLOW ##############################

    mlflow_config = config["mlflow_config"]
    remote_server_uri = mlflow_config["remote_server_uri"]

    mlflow.set_tracking_uri(remote_server_uri)
    mlflow.set_experiment(mlflow_config["experiment_name"])

    is_remote = mlflow_config["is_remote"]
    if not is_remote:
        with mlflow.start_run(run_name=mlflow_config["run_name"]) as mlops_run:
            model = generate_model(train_set, test_set, image_shape)
            y_pred = model.predict_generator(test_set)
            y_pred = [1 if y > 0.5 else 0 for y in y_pred]  # Converting probabilities to class labels
            test_y = test_set.classes

            accuracy, precision, recall, f1score = accuracymeasures(test_y, y_pred, 'weighted')

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1score)

            tracking_url_type_store = urlparse(mlflow.get_artifact_uri()).scheme

            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(
                    model,
                    "model",
                    registered_model_name=mlflow_config["registered_model_name"])
            else:
                # Log the model to the local directory...
                mlflow.sklearn.log_model(model, "model")
                # Get the URI of the model artifact
                model_uri = os.path.join(mlflow.get_artifact_uri(), "model")
                # Load the model from the local directory
                mlflow.sklearn.load_model(model_uri=model_uri)

        joblib.dump(model, model_dir)
        joblib.dump(model, web_model_dir)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    train_and_evaluate(config_path=parsed_args.config)
    # test
