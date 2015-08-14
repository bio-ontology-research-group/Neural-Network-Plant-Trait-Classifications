'''
    GPU run command:
        THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python cnn.py
        THEANO_FLAGS='cuda.root=/usr/local/cuda'=mode=FAST_RUN,device=gpu,floatX=float32 python cnn.py
    CPU run command:
        python cnn.py
'''

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import *
from keras.utils import np_utils, generic_utils
from os.path import expanduser
import  imp, numpy as np, os.path as path

image_preprocesser = imp.load_source('preprocess', '../../pyvec/pyvec/images/image_preprocessor.py')
dataset_getter = imp.load_source('dataset', '../../pyvec/pyvec/images/dataset.py')

home_directory = expanduser("~")
custom_dir = "preProcessed/"

# Data Parameters
custom_height = 64
custom_width = 64
directory = home_directory + "/datasets/colours/labeledFolders"
save_path = path.abspath(path.join(directory +"/../", custom_dir))

num_classes = 9
split = 0.9 #Split training and validation (90% for training, 10% validation)

# Training Parameters
np.random.seed(1337) # Reproducable results :)
num_epoch = 40
batch_size = 100


# Already done: image_preprocesser.preprocess(directory, custom_dir, custom_height, custom_width)

X_train, Y_train, X_val, Y_val = dataset_getter.vectorise(save_path,num_classes,custom_height,
                                                                custom_width, split)
y_train = np_utils.to_categorical(Y_train, num_classes)
y_val = np_utils.to_categorical(Y_val, num_classes)

model = Sequential()

model.add(Convolution2D(custom_height, 3, 3, 3, border_mode='full'))
model.add(Activation('relu'))
model.add(Convolution2D(custom_height, custom_width, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(poolsize=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(65536, 128))
model.add(Activation('relu'))
model.add(Dropout(0.5))

model.add(Dense(128, num_classes))
model.add(Activation('softmax'))

rms = Adadelta()
model.compile(loss='categorical_crossentropy', optimizer=rms)

nb_train = len(Y_train)
nb_validation = len(Y_val)
print( 'train samples:',nb_train, 'validation samples:',nb_validation)

best_accuracy = 0.0

for e in range(num_epoch):
    print ('Epoch ', e)
    print ('Training...')
    batch_num = len(y_train)/batch_size
    progbar = generic_utils.Progbar(X_train.shape[0])
    for i in range(batch_num):
        train_loss,train_accuracy = model.train_on_batch(X_train[i*batch_size:(i+1)*batch_size], Y_train[i*batch_size:(i+1)*batch_size], accuracy=True)
        progbar.add(batch_size, values=[("train loss", train_loss), ("train accuracy:", train_accuracy)] )

    print('\nRunning a little validation...')
    val_loss,val_accuracy = model.evaluate(X_val, y_val, batch_size=100,show_accuracy=True)

    if best_accuracy < val_accuracy:
        best_accuracy = val_accuracy
