from flask import Flask, jsonify, request
app = Flask(__name__)

import numpy as np
import pickle
import urllib.parse
from keras.preprocessing.sequence import pad_sequences

from tensorflow import keras

model = keras.models.load_model('20180803_ognl_model.h5', compile=False)
max_len = model.input.shape[1]

# If you run this code on the other computer, you might need to remove commentout below.
# Sometimes mode.predict function does not load correctly.
# import numpy as ap
# X = np.zeros((10, max_len))
# model.predict(X, batch_size=32)

with open('20180803_ognl_token.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)
with open('20180803_ognl_encode.pickle', 'rb') as handle:
    encoder = pickle.load(handle)

@app.route('/preds/', methods=['GET'])
def preds():
    # loading
    reqstr = request.args.get('str', '')
    reqstr = urllib.parse.quote(reqstr, safe='')
    reqstr = [reqstr]
    response = jsonify()
    req_mat = tokenizer.texts_to_sequences(reqstr)
    req_mat = pad_sequences(req_mat, maxlen=int(max_len))
    prediction = model.predict(req_mat)
    predicted_label = encoder.classes_[np.argmax(prediction)]

    # if normal
    if predicted_label == 'normal':
        response.status_code = 201
    # if attack
    elif predicted_label == 'attack':
        response.status_code = 202

    # save
    with open('request.log', mode='a') as f:
        f.write(str(response.status_code) + str(prediction) + ',' + str(reqstr) + '\n')

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
