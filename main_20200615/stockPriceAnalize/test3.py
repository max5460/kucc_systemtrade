from keras.models import load_model


predictModel = load_model('test.h5')

a = predictModel.predict
