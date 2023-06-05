import numpy as np
from frank_wolfe import *

def expected_frank_wolfe_wrapper(predictions: csr_matrix, loss_func, k: int = 5, seed: int = 0, **kwargs):
    classifiers, classifier_weights = frank_wolfe(predictions, predictions, max_iters=20, loss_func=loss_func, k=5)
    y_pred = predict_top_k_for_classfiers(predictions, classifiers, classifier_weights, k=k, seed=seed)
    return y_pred


def expected_frank_wolfe_macro_recall(predictions: csr_matrix, k: int = 5, seed: int = 0, **kwargs):
    return expected_frank_wolfe_wrapper(predictions, fw_macro_recall, k=k, seed=seed)


def expected_frank_wolfe_macro_precision(predictions: csr_matrix, k: int = 5, seed: int = 0, **kwargs):
    return expected_frank_wolfe_wrapper(predictions, fw_macro_precision, k=k, seed=seed)


def expected_frank_wolfe_macro_f1(predictions: csr_matrix, k: int = 5, seed: int = 0, **kwargs):
    return expected_frank_wolfe_wrapper(predictions, fw_macro_f1, k=k, seed=seed)
