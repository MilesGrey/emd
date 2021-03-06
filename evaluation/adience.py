from pathlib import Path
from typing import List, Callable, Union, Type

from tensorflow.keras.activations import linear, softmax
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from data_handlers.adience import get_adience_info, ADIENCE_TRAIN_FOLDS_INFO_FILES, \
    ADIENCE_VALIDATION_FOLDS_INFO_FILES, ADIENCE_CLASSES
from data_handlers.data_set_info import DatasetName
from data_handlers.generators import custom_data_loading
from models.constants import LEARNING_RATES
from models.evaluation_model import EvaluationModel


def evaluate_adience_model(
        evaluation_model: Type[EvaluationModel],
        learning_rate_index: int,
        fold_index: int,
        loss_function: Callable,
        final_activation: Union[softmax, linear],
        ground_distance_path: Path = None,
        **loss_function_kwargs
):
    model = evaluation_model(
        number_of_classes=len(ADIENCE_CLASSES),
        dataset_name=DatasetName.ADIENCE,
        final_activation=final_activation,
        loss_function=loss_function,
        learning_rate=LEARNING_RATES[learning_rate_index],
        fold_index=fold_index,
        ground_distance_path=ground_distance_path,
        **loss_function_kwargs
    )
    evaluate_adience_fold(
        model=model,
        train_fold_info_files=ADIENCE_TRAIN_FOLDS_INFO_FILES[fold_index],
        validation_fold_info_file=ADIENCE_VALIDATION_FOLDS_INFO_FILES[fold_index]
    )


def evaluate_adience_fold(
        model: EvaluationModel,
        train_fold_info_files: List[Path],
        validation_fold_info_file: Path
) -> None:
    train_info, validation_info = get_adience_info(
        train_fold_info_files=train_fold_info_files,
        validation_fold_info_file=validation_fold_info_file
    )
    train_generator, validation_generator = custom_data_loading(
        train_info=train_info,
        validation_info=validation_info
    )
    evaluate(
        model=model,
        train_generator=train_generator,
        validation_generator=validation_generator
    )


def evaluate(
        model: EvaluationModel,
        train_generator: ImageDataGenerator,
        validation_generator: ImageDataGenerator
) -> None:
    model.train(
        x=train_generator,
        epochs=160,
        validation_data=validation_generator,
        steps_per_epoch=None,
        validation_steps=None
    )
