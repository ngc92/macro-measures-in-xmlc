# simple tests for macro precision at k
# all code uses dense matrices, so it won't scale to really large problems
# first index is always instance, second index is always label

import numpy as np
from scipy.sparse import csr_matrix
from typing import Union

from metrics import macro_precision
from sparse_prediction import *


def _make_filler(num_labels: int, k: int):
    all_labels = set(range(num_labels))

    def filler(target: np.ndarray, already_selected: np.ndarray):
        free_labels = list(all_labels - set(already_selected))
        additional = np.random.choice(free_labels, k - len(already_selected), replace=False)
        target[already_selected] = 1.0
        target[additional] = 1.0

    return filler


def predict_random_at_k(predictions: np.ndarray, k: int = 5):
    """
    Randomly select among the true labels. A very simple baseline
    that requires 0/1 inputs.
    """
    ni, nl = predictions.shape
    result = np.zeros_like(predictions)
    filler = _make_filler(nl, k)
    for i in range(ni):
        lbl_at_i = np.nonzero(predictions[i, :])[0]
        if len(lbl_at_i) > k:
            active = np.random.choice(lbl_at_i, k, replace=False)
            result[i, active] = 1.0
        else:
            filler(result[i, :], lbl_at_i)
    return result


def random_at_k(predictions: np.ndarray, k: int = 5):
    """
    Select predicted labels completely randomly, ignoring whether they are true/false.
    """
    ni, nl = predictions.shape
    result = np.zeros_like(predictions)
    all_labels = list(range(nl))
    for i in range(ni):
        additional = np.random.choice(all_labels, k, replace=False)
        result[i, additional] = 1.0
    return result


def block_coordinate_ascent(predictions: np.ndarray, k: int = 5, epsilon: float = 0.001):
    """
    An inefficient implementation of the block coordinate-descent idea for optimizing
    macroP@k. The implementation is designed to be "obviously correct", and sacrifices
    potential performance increases for that.
    In a real implementation, we would not re-compute `a` and `b` from scratch in each
    step.
    """
    ni, nl = predictions.shape

    # initialize the prediction variable with some feasible value
    result = random_at_k(predictions, k)
    old_p = macro_precision(predictions, result)
    while True:
        order = np.arange(ni)
        np.random.shuffle(order)
        for i in order:
            # important to be precise here with the sum,
            # if we do not exclude the current instance,
            # we might not select steps that improve the
            # result.
            b = np.sum(result[:i], axis=0)
            b += np.sum(result[i+1:], axis=0) + epsilon
            a = np.sum(result[:i] * predictions[:i], axis=0)
            a += np.sum(result[i+1:] * predictions[i + 1:], axis=0)
            eta = predictions[i, :]
            g = (b * eta - a) / (b**2)
            top_k = np.argpartition(-g, k)[:k]
            # old_v = macro_precision(labels, result, epsilon=epsilon)
            result[i, :] = 0.0
            result[i, top_k] = 1.0
            # new_v = macro_precision(labels, result, epsilon=epsilon)
            # assert new_v >= old_v - 1e-6, (old_v, new_v, g)
        new_p = macro_precision(predictions, result, epsilon=epsilon)
        print(old_p, " -> ", new_p)
        if new_p <= old_p:
            break
        old_p = new_p

    return result


def block_coordinate_ascent_fast(predictions: np.ndarray, k: int = 5, *, epsilon: float = 0.001,
                                 tolerance: float = 1e-4):
    """
    An efficient implementation of the block coordinate-descent idea for optimizing
    macroP@k.
    """
    ni, nl = predictions.shape

    # initialize the prediction variable with some feasible value
    result = predict_random_at_k(predictions, k)
    old_p = macro_precision(predictions, result)
    while True:
        order = np.arange(ni)
        np.random.shuffle(order)
        # calculate a and b for each iteration, to prevent numerical errors
        # from accumulating too much
        b = np.sum(result, axis=0) + epsilon
        a = np.sum(result * predictions, axis=0)

        for i in order:
            # adjust a and b locally
            a -= result[i]
            b -= result[i] * predictions[i]

            # calculate gain and selection
            eta = predictions[i, :]
            g = (b * eta - a) / (b*(b + 1))
            top_k = np.argpartition(-g, k)[:k]

            # update predictions
            result[i, :] = 0.0
            result[i, top_k] = 1.0

            # update a and b
            a += result[i]
            b += result[i] * predictions[i]

        new_p = macro_precision(predictions, result, epsilon=epsilon)
        if new_p <= old_p + tolerance:
            break
        old_p = new_p

    return result


def weighted_per_instance(prediction: Union[np.ndarray, csr_matrix], weights: np.ndarray, k: int = 5):
    if isinstance(prediction, np.ndarray):
        # Invoke original implementation of Erik
        return np_weighted_per_instance(prediction, weights, k=k)
    elif isinstance(prediction, csr_matrix):
        # Invoke implementation for sparse matrices
        return csr_weighted_per_instance(prediction, weights, k=k)


def np_weighted_per_instance(prediction: np.ndarray, weights: np.ndarray, k: int = 5):
    ni, nl = prediction.shape
    assert weights.shape == (nl,)

    result = np.zeros((ni, nl), np.float32)

    for i in range(ni):
        eta = prediction[i, :]
        g = eta * weights
        top_k = np.argpartition(-g, k)[:k]
        result[i, top_k] = 1.0
    return result


def csr_weighted_per_instance(prediction: csr_matrix, weights: np.ndarray, k: int = 5):
    # Since many numpy functions are not supported for sparse matrices,
    # we need to implement it ourselves, and since we are using Python, it will be slooooow...
    # Here I use Numba to have a fast implementation (C-like performance)
    ni, nl = prediction.shape
    data, indices, indptr = sparse_weighted_per_instance(prediction.data, prediction.indices, prediction.indptr, weights, ni, nl, k)
    return csr_matrix((data, indices, indptr), shape=prediction.shape)


def optimal_macro_recall(prediction: np.ndarray, k: int = 5, *, marginal):
    return weighted_per_instance(prediction, 1.0 / (marginal + 0.0001), k=k)


def log_weighted_instance(prediction: np.ndarray, k: int = 5, *, marginal):
    weight = -np.log(marginal + 0.0001)
    return weighted_per_instance(prediction, weight, k=k)


def sqrt_weighted_instance(prediction: np.ndarray, k: int = 5, *, marginal):
    weight = 1.0 / np.sqrt(marginal + 0.0001)
    return weighted_per_instance(prediction, weight, k=k)


def power_law_weighted_instance(prediction: np.ndarray, k: int = 5, *, marginal, beta):
    weight = 1.0 / (marginal + 0.0001)**beta
    return weighted_per_instance(prediction, weight, k=k)


def optimal_instance_precision(prediction: np.ndarray, k: int = 5):
    ni, nl = prediction.shape
    weights = np.ones((nl,), dtype=np.float32)
    return weighted_per_instance(prediction, weights, k=k)


def greedy_coverage(prediction: np.ndarray, k: int = 5, *, decay=1.0):
    ni, nl = prediction.shape

    f = np.zeros((nl,), dtype=np.float32)
    result = np.zeros((ni, nl), np.float32)
    # convert to log space. Add some epsilon here so things work with 0/1 probabilities
    log_p = np.log(np.maximum(prediction, 1e-5))
    log_1mp = np.log(np.maximum(1.0 - prediction, 1e-5))

    for i in range(ni):
        f *= decay

        # determine gain
        g = f + log_p[i, :]

        # select top gain labels
        top_k = np.argpartition(-g, k)[:k]
        result[i, top_k] = 1.0

        # update estimate
        for j in top_k:
            f[j] += log_1mp[i, j]

    return result


def greedy_precision(predictions: np.ndarray, k: int = 5, *, epsilon: float = 0.001):
    """
    An efficient implementation of the block coordinate-descent idea for optimizing
    macroP@k.
    """
    ni, nl = predictions.shape

    # initialize the prediction variable with some feasible value
    result = np.zeros((ni, nl), np.float32)
    order = np.arange(ni)
    np.random.shuffle(order)
    # calculate a and b for each iteration, to prevent numerical errors
    # from accumulating too much
    b = np.sum(result, axis=0) + epsilon
    a = np.sum(result * predictions, axis=0)

    for i in order:
        # calculate gain and selection
        eta = predictions[i, :]
        g = (b * eta - a) / (b*(b + 1))
        top_k = np.argpartition(-g, k)[:k]

        # update predictions
        result[i, :] = 0.0
        result[i, top_k] = 1.0

        # update a and b
        a += result[i]
        b += result[i] * predictions[i]

    return result


def block_coordinate_coverage(predictions: np.ndarray, k: int = 5, *, tolerance: float = 1e-4):
    """
    An efficient implementation of the block coordinate-descent idea for optimizing
    macroP@k.
    """
    ni, nl = predictions.shape

    # initialize the prediction variable with some feasible value
    result = predict_random_at_k(predictions, k)
    f = np.product(1 - result * predictions, axis=0)
    old_cov = 1 - np.mean(f)

    predictions = np.minimum(predictions, 1 - 1e-5)

    while True:
        order = np.arange(ni)
        np.random.shuffle(order)
        f = np.product(1 - result * predictions, axis=0)

        for i in order:
            # adjust f locally
            f /= 1 - result[i] * predictions[i]

            # calculate gain and selection
            eta = predictions[i, :]
            g = f * eta
            top_k = np.argpartition(-g, k)[:k]

            # update predictions
            result[i, :] = 0.0
            result[i, top_k] = 1.0

            # update f
            f *= (1 - result[i] * predictions[i])

        new_cov = 1 - np.mean(f)
        # print(f"{old_cov} -> {new_cov}")
        # print(macro_abandonment(predictions, result))
        if new_cov <= old_cov + tolerance:
            break
        old_cov = new_cov

    # print(macro_abandonment(predictions, result))

    return result


def macro_population_cm_risk(probabilities: np.ndarray, *, measure: callable, k: int = 5, tolerance: float = 1e-4):
    ni, nl = probabilities.shape

    # initialize the prediction variable with some feasible value
    result = random_at_k(probabilities, k)
    #result = optimal_instance_precision(probabilities, k)
    # result = optimal_macro_recall(probabilities, k, marginal=np.mean(probabilities, axis=0))

    while True:
        order = np.arange(ni)
        np.random.shuffle(order)
        # calculate a and b for each iteration, to prevent numerical errors
        # from accumulating too much
        Etp = np.sum(result * probabilities, axis=0)
        Efp = np.sum(result * (1-probabilities), axis=0)
        Efn = np.sum((1-result) * probabilities, axis=0)
        old_score = np.mean(measure(Etp / ni, Efp / ni, Efn / ni))

        for i in order:
            # adjust a and b locally
            eta = probabilities[i, :]
            Etp -= result[i] * eta
            Efp -= result[i] * (1-eta)
            Efn -= (1-result[i]) * eta

            # calculate gain and selection
            Etpp = Etp + eta
            Efpp = Efp + (1-eta)
            Efnn = Efn + eta
            p_score = measure(Etpp / ni, Efpp / ni, Efn / ni)
            n_score = measure(Etp / ni, Efp / ni, Efnn / ni)
            gains = p_score - n_score
            top_k = np.argpartition(-gains, k)[:k]

            # update predictions
            result[i, :] = 0.0
            result[i, top_k] = 1.0

            # update a and b
            Etp += result[i] * eta
            Efp += result[i] * (1 - eta)
            Efn += (1 - result[i]) * eta

        new_score = np.mean(measure(Etp / ni, Efp / ni, Efn / ni))
        print(old_score, "->", new_score)
        if new_score <= old_score + tolerance:
            break

    return result
