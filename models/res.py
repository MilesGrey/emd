from typing import Union, ClassVar

import numpy as np

from tensorflow.keras.activations import softmax, linear
from tensorflow.keras.layers import Conv2D, Layer, BatchNormalization, Dense, ReLU, AvgPool2D, Flatten
from tensorflow import TensorShape

from models.evaluation_model import EvaluationModel


class Res(EvaluationModel):
    """
    RES model. Reference: S. Zagoruyko and N. Komodakis. "Wide residual networks", 2016.
    """

    _MODEL_NAME: ClassVar[str] = 'RES'

    def _build_model(
            self,
            number_of_classes: int,
            final_activation: Union[softmax, linear]
    ):
        self.wrn = WideResidualNetwork(
            group_size=13,
            activation=ReLU,
            input_shape=(227, 227, 3)
        )
        self.flatten = Flatten()
        self.dense3 = Dense(number_of_classes, activation=final_activation)


class Resf(EvaluationModel):

    _MODEL_NAME: ClassVar[str] = 'RES_f'

    def _build_model(
            self,
            number_of_classes: int,
            final_activation: Union[softmax, linear]
    ):
        pass


class BasicLayer(Layer):

    def __init__(self, sub_layers, stride, filters, k, **kwargs):
        super(BasicLayer, self).__init__(**kwargs)
        self.sub_layers = sub_layers
        self.stride = stride
        self.filters = filters
        self.k = k

    def call(self, inputs, **kwargs):
        x = self.sub_layers[0](inputs, **kwargs)
        for layer in self.sub_layers[1:]:
            x = layer(x, **kwargs)
        return x

    def compute_output_shape(self, input_shape):
        return TensorShape((
            input_shape[0],
            input_shape[1] // self.stride,
            input_shape[2] // self.stride,
            self.filters * self.k
        ))


class ConvolutionBlock(BasicLayer):

    def __init__(self, filters, kernel_size, stride=1, activation=ReLU, k=1, **kwargs):
        super(ConvolutionBlock, self).__init__(
            sub_layers=[
                BatchNormalization(),
                activation(),
                Conv2D(
                    filters=filters * k,
                    kernel_size=kernel_size,
                    strides=stride,
                    padding='same'
                )
            ],
            stride=stride,
            filters=filters,
            k=k,
            **kwargs
        )

    def call(self, inputs, **kwargs):
        return super(ConvolutionBlock, self).call(inputs, **kwargs)

    def compute_output_shape(self, input_shape):
        return super(ConvolutionBlock, self).compute_output_shape(input_shape)


class BottleneckBlock(BasicLayer):

    def __init__(self, filters, stride=1, activation=ReLU, k=1, **kwargs):
        super(BottleneckBlock, self).__init__(
            sub_layers=[
                ConvolutionBlock(
                    filters=filters * k,
                    kernel_size=(1, 1),
                    stride=stride,
                    activation=activation
                ),
                ConvolutionBlock(
                    filters=filters * k,
                    kernel_size=(3, 3),
                    activation=activation
                ),
                ConvolutionBlock(
                    filters=filters * k,
                    kernel_size=(1, 1),
                    activation=activation
                )
            ],
            stride=stride,
            filters=filters,
            k=k,
            **kwargs
        )

    def call(self, inputs, **kwargs):
        return super(BottleneckBlock, self).call(inputs, **kwargs)

    def compute_output_shape(self, input_shape):
        return super(BottleneckBlock, self).compute_output_shape(input_shape)


class Group(BasicLayer):

    def __init__(self, n, filters, stride=1, activation=ReLU, k=1, **kwargs):
        super(Group, self).__init__(
            sub_layers=[BottleneckBlock(filters, stride, activation, k)]
            + [BottleneckBlock(filters, activation=activation, k=k) for _ in range(n - 1)],
            stride=stride,
            filters=filters,
            k=k,
            **kwargs
        )

    def call(self, inputs, **kwargs):
        return super(Group, self).call(inputs, **kwargs)

    def compute_output_shape(self, input_shape):
        return super(Group, self).compute_output_shape(input_shape)


class WideResidualNetwork(Layer):

    FILTER_SIZES = [16, 16, 32, 64]
    STRIDES = [4, 1, 2, 2]

    def __init__(self, input_shape, group_size, pool_size=8, activation=ReLU, k=1, **kwargs):
        super(WideResidualNetwork, self).__init__(input_shape=input_shape, dynamic=True, **kwargs)
        self.groups = [
            Conv2D(
                input_shape=input_shape,
                filters=WideResidualNetwork.FILTER_SIZES[0],
                kernel_size=(3, 3),
                strides=WideResidualNetwork.STRIDES[0],
                padding='same'
            )
        ]
        self.groups.extend([
            Group(
                n=group_size,
                filters=WideResidualNetwork.FILTER_SIZES[i],
                stride=WideResidualNetwork.STRIDES[i],
                activation=activation,
                k=k
            )
            for i in range(1, len(WideResidualNetwork.FILTER_SIZES))
        ])
        self.groups.append(AvgPool2D(pool_size=pool_size))
        self.pool_size = pool_size

    def call(self, inputs, **kwargs):
        x = self.groups[0](inputs)
        for group in self.groups[1:]:
            x = group(x)
        return x

    def compute_output_shape(self, input_shape):
        stride_product = np.product(WideResidualNetwork.STRIDES)
        return TensorShape((
            input_shape[0],
            input_shape[1] // (stride_product * self.pool_size),
            input_shape[2] // (stride_product * self.pool_size),
            WideResidualNetwork.FILTER_SIZES[-1]
        ))
