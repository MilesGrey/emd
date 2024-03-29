from typing import Union, ClassVar

from tensorflow.keras import Input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Dropout, Layer, Concatenate
from tensorflow.keras.activations import relu, softmax, linear
from tensorflow.keras.regularizers import l2
from tensorflow.python.ops.nn_ops import local_response_normalization

from models.evaluation_model import EvaluationModel


class Alxs(EvaluationModel):
    """
    ALXs model. Reference: E. Eidinger, R. Enbar, and T. Hassner. "Age andgender estimation of unfiltered faces", 2014.
    """

    _MODEL_NAME: ClassVar[str] = 'ALXs'

    def _build_model(
            self,
            number_of_classes: int,
            final_activation: Union[softmax, linear]
    ):
        self.conv1 = Conv2D(
            input_shape=(227, 227, 3),
            filters=96,
            kernel_size=(7, 7),
            strides=4,
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=relu
        )
        self.pool1 = MaxPool2D(
            pool_size=(3, 3),
            padding='same',
            strides=2
        )
        self.normalization1 = LocalResponseNormalization()
        self.conv2 = Conv2D(
            filters=256,
            kernel_size=(5, 5),
            padding='same',
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=relu
        )
        self.pool2 = MaxPool2D(
            pool_size=(3, 3),
            padding='same',
            strides=2
        )
        self.normalization2 = LocalResponseNormalization()
        self.conv3 = Conv2D(
            filters=384,
            kernel_size=(3, 3),
            padding='same',
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=relu
        )
        self.pool3 = MaxPool2D(
            pool_size=(3, 3),
            padding='same',
            strides=2
        )
        self.flatten = Flatten()
        self.dense1 = Dense(
            units=512,
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=relu
        )
        self.dropout1 = Dropout(0.5)
        self.dense2 = Dense(
            units=512,
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=relu
        )
        self.dropout2 = Dropout(0.5)
        self.dense3 = Dense(
            units=number_of_classes,
            kernel_regularizer=l2(1e-20),
            bias_regularizer=l2(1e-20),
            activation=final_activation
        )


class Alx(EvaluationModel):
    """
    ALX model. Reference: A. Krizhevsky, I. Sutskever, and G. E. Hinton. "Imagenet classification with deep
    convolutional neural networks", 2012.
    """

    _MODEL_NAME: ClassVar[str] = 'ALX'

    def _build_model(
            self,
            number_of_classes: int,
            final_activation: Union[softmax, linear]
    ):
        inputs = Input(
            shape=(227, 227, 3)
        )
        convolution_1a = Conv2D(
            filters=48,
            kernel_size=(11, 11),
            padding='same',
            strides=4,
            activation=relu
        )(inputs)
        convolution_1b = Conv2D(
            filters=48,
            kernel_size=(11, 11),
            padding='same',
            strides=4,
            activation=relu
        )(inputs)
        normalized_1a = LocalResponseNormalization()(convolution_1a)
        normalized_1b = LocalResponseNormalization()(convolution_1b)
        max_pooling_1a = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(normalized_1a)
        max_pooling_1b = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(normalized_1b)
        convolution_2a = Conv2D(
            filters=128,
            kernel_size=(5, 5),
            padding='same',
            activation=relu
        )(max_pooling_1a)
        convolution_2b = Conv2D(
            filters=128,
            kernel_size=(5, 5),
            padding='same',
            activation=relu
        )(max_pooling_1b)
        normalized_2a = LocalResponseNormalization()(convolution_2a)
        normalized_2b = LocalResponseNormalization()(convolution_2b)
        max_pooling_2a = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(normalized_2a)
        max_pooling_2b = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(normalized_2b)
        concatenated_1 = Concatenate()([max_pooling_2a, max_pooling_2b])
        convolution_3a = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(concatenated_1)
        convolution_3b = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(concatenated_1)
        convolution_4a = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(convolution_3a)
        convolution_4b = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(convolution_3b)
        convolution_5a = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(convolution_4a)
        convolution_5b = Conv2D(
            filters=192,
            kernel_size=(3, 3),
            padding='same',
            activation=relu
        )(convolution_4b)
        max_pooling_2a = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(convolution_5a)
        max_pooling_2b = MaxPool2D(
            pool_size=(3, 3),
            strides=2,
            padding='same',
        )(convolution_5b)
        concatenated_2 = Concatenate()(max_pooling_2a, max_pooling_2b)
        flattened_1 = Flatten()(concatenated_2)
        dense_1a = Dense(
            units=2048,
            activation=relu
        )(flattened_1)
        dense_1b = Dense(
            units=2048,
            activation=relu
        )(flattened_1)
        dropped_1a = Dropout(rate=0.5)(dense_1a)
        dropped_1b = Dropout(rate=0.5)(dense_1b)
        dense_2a = Dense(
            units=2048,
            activation=relu
        )(dropped_1a)
        dense_2b = Dense(
            units=2048,
            activation=relu
        )(dropped_1b)
        dropped_2a = Dropout(rate=0.5)(dense_2a)
        dropped_2b = Dropout(rate=0.5)(dense_2b)
        concatenated_3 = Concatenate()([dropped_2a, dropped_2b])
        outputs = Dense(
            units=number_of_classes,
            activation=softmax
        )(concatenated_3)
        self.alxs = Model(
            inputs=inputs,
            outputs=outputs
        )


class LocalResponseNormalization(Layer):

    def __init__(self, n=5, alpha=0.0001, beta=0.75, k=2, **kwargs):
        self.n = n
        self.alpha = alpha
        self.beta = beta
        self.k = k
        super(LocalResponseNormalization, self).__init__(**kwargs)

    def call(self, inputs, **kwargs):
        return local_response_normalization(
            input=inputs,
            depth_radius=self.n,
            bias=self.k,
            alpha=self.alpha,
            beta=self.beta
        )

    def compute_output_shape(self, input_shape):
        return input_shape
