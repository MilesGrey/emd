from abc import ABC, abstractmethod
from typing import ClassVar, Callable, Union, List

from tensorflow.keras.metrics import Metric
from tensorflow.keras import Model
from tensorflow.keras.activations import linear, softmax
from tensorflow.keras.metrics import categorical_accuracy
from tensorflow.keras.optimizers import SGD, Optimizer

from data_handlers.data_set_info import DatasetName
from evaluation.logging import get_checkpoint_file, get_tensorboard_callback
from loss_functions.emd import EmdWeightHeadStart
from metrics.accuracy import one_off_accuracy


class EvaluationModel(ABC):

    _OPTIMIZER: ClassVar[Optimizer] = SGD
    _OPTIMIZER_MOMENTUM: ClassVar[float] = 0.98
    _METRICS: ClassVar[List[Metric]] = [
        categorical_accuracy,
        one_off_accuracy
    ]
    model: Model = None

    def __init__(
            self,
            number_of_classes: int,
            dataset_name: DatasetName,
            final_activation: Union[softmax, linear],
            loss_function: Callable,
            learning_rate: float,
            **loss_function_kwargs,
    ):
        self.learning_rate = learning_rate
        self.dataset_name = dataset_name

        self._build_model(
            number_of_classes=number_of_classes,
            final_activation=final_activation
        )
        self._compile_model(
            loss_function=loss_function,
            **loss_function_kwargs
        )

    @abstractmethod
    def _build_model(
            self,
            number_of_classes: int,
            final_activation: Union[softmax, linear]
    ):
        pass

    def _get_second_to_last_layer(self):
        return self.model.layers[-2]

    def _compile_model(
            self,
            loss_function: Callable,
            **loss_function_kwargs
    ):
        self.emd_weight_head_start = EmdWeightHeadStart()
        self.model.compile(
            loss=loss_function(
                second_to_last_layer=self._get_second_to_last_layer(),
                emd_weight_head_start=self.emd_weight_head_start,
                **loss_function_kwargs
            ),
            optimizer=self._OPTIMIZER(
                learning_rate=self.learning_rate,
                momentum=self._OPTIMIZER_MOMENTUM
            ),
            metrics=self._METRICS,
            run_eagerly=True
        )

    def predict(self, **kwargs):
        return self.model.predict(**kwargs)

    def fit(self, **kwargs):
        return self.model.fit(
            callbacks=[
                self.emd_weight_head_start,
                get_checkpoint_file(
                    data_set_name=self.dataset_name,
                    learning_rate=self.learning_rate
                ),
                get_tensorboard_callback(
                    data_set_name=self.dataset_name,
                    learning_rate=self.learning_rate
                )
            ],
            **kwargs
        )
