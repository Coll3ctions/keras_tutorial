import scipy.io as io
import numpy as np
import theano.tensor as T
import os
import matplotlib.pyplot as plt

from sklearn import preprocessing as pre
from sklearn import metrics
from sklearn import cross_validation as c_v
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
from keras.models import model_from_json
from keras.regularizers import l2, activity_l2
from keras.layers.normalization import BatchNormalization

earlystopping = EarlyStopping(monitor='val_loss', patience=4, verbose=1)

ironic  = 'ironic.txt'
regular ='regular.txt'

targets = np.empty([1,])
full_data = np.empty([1,])


ironic_file  = open(ironic, 'r')
regular_file = open(regular, 'r')

max_len = 0
samples = 0

while True:
    curr_line = ironic_file.readline()
    if not curr_line:
        break

    samples = samples + 1
    if len(curr_line) > max_len:
        max_len = len(curr_line)

ironic_num = samples

while True:
    curr_line = regular_file.readline()
    if not curr_line:
        break

    samples = samples + 1
    if len(curr_line) > max_len:
        max_len = len(curr_line)

regular_num = samples - ironic_num

ironic_file.close()
regular_file.close()

ironic_file  = open(ironic, 'r')
regular_file = open(regular, 'r')
        
print max_len
print ironic_num, regular_num 

data = np.empty([samples,max_len])
index = 0
while True:
    curr_line = ironic_file.readline().replace('\n', '')
    if not curr_line:
        break
    
    curr_line = map(int, curr_line.split(' '))
    diff = max_len - len(curr_line)
    data[index, :] = np.concatenate((curr_line, np.zeros(diff,)))
    index = index + 1

while True:
    curr_line = regular_file.readline().replace('\n', '')
    if not curr_line:
        break
    
    curr_line = map(int, curr_line.split(' '))
    diff = max_len - len(curr_line)
    data[index, :] = np.concatenate((curr_line, np.zeros(diff,)))

    index = index + 1

targets = np.concatenate((np.ones(ironic_num, ), np.zeros(regular_num, )))

data = data.reshape(data.shape[0], data.shape[1], 1)

print targets.shape
print data.shape

skf = c_v.StratifiedKFold(targets, n_folds=5, shuffle=True)

for train_index, test_index in skf:
    #print("TRAIN:", train_index, "TEST:", test_index)
    X_train, X_test = data[train_index], data[test_index]
    y_train, y_test = targets[train_index], targets[test_index]

    model = Sequential()

    model.add(Convolution1D(nb_filter=75, filter_length=3, activation='relu', input_dim=1, input_length=max_len))
    model.add(Dropout(0.5))
    model.add(MaxPooling1D(pool_length=8))

    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(30, activation='relu'))
    model.add(Dropout(0.5)) 

    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

    history = model.fit(X_train, y_train, batch_size=25, nb_epoch=50,
                        validation_split=0.2)

    loss = history.history['loss']
    plt.plot(loss)
    plt.show()

    
    score, acc = model.evaluate(X_test, y_test, batch_size=8, show_accuracy=True)
    
    print ('Test score:', score)
    print ('Test accuracy:', acc)

    out = model.predict(X_test, batch_size=8, verbose=1)

    classes = model.predict_classes(X_test, batch_size=8, verbose=1)
    print metrics.confusion_matrix(y_test.astype(int), classes)
    print metrics.classification_report(y_test.astype(int), classes)
