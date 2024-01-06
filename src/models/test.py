import joblib
from keras.src.preprocessing.image import ImageDataGenerator

if __name__ == "__main__":
    test_data_path = "data/processed/casting_data/test"
    image_gen = ImageDataGenerator(rescale=1 / 255, zoom_range=0.1, brightness_range=[0.9, 1.0])
    image_shape = (300, 300, 1)  # 300 × 300、graysclaed (full-color : 3)
    batch_size = 32
    test_set = image_gen.flow_from_directory(test_data_path,
                                             target_size=image_shape[:2],
                                             color_mode="grayscale",
                                             classes={'def_front': 0, 'ok_front': 1},
                                             batch_size=batch_size,
                                             class_mode='binary',
                                             shuffle=False,
                                             seed=0)


    model = joblib.load("model/model.joblib")
    y_pred = model.predict(test_set)