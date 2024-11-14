from ...pyqt_base import *
from ...ui_common import *
from ...nn_base import *
from ..pyqt import *
from ..thread import *

import tensorflow as tf
# from tensorflow import keras
from keras import optimizers
from keras.layers import Input, Dense, Multiply, Layer
from keras.models import Model
import keras.backend as K