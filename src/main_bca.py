import numpy as np

from metrics import *
from data import *
from weighted_prediction import *
from bca_prediction import *
from utils_misc import *

import sys
import click

RECALCULATE_RESUTLS = False
RECALCULATE_PREDICTION = False
K = (1, 3, 5, 10)

METRICS = {
    "mC": macro_abandonment,
    "iC": instance_abandonment,
    "mP": macro_precision,
    "iP": instance_precision,
    "mR": macro_recall,
    "iR": instance_recall,
    "mF": macro_f1,
    "iF": instance_f1,
}


METHODS = {
    # Instance-wise measures / baselines
    # "random": (predict_random_at_k,{}),
    "optimal-instance-prec": (optimal_instance_precision, {}),
    "optimal-instance-ps-prec": (inv_propensity_weighted_instance, {}),
    #"power-law-with-beta=0.875": (power_law_weighted_instance, {"beta": 0.875}),
    "power-law-with-beta=0.75": (power_law_weighted_instance, {"beta": 0.75}),
    "power-law-with-beta=0.5": (power_law_weighted_instance, {"beta": 0.5}),
    "power-law-with-beta=0.25": (power_law_weighted_instance, {"beta": 0.25}),
    #"power-law-with-beta=0.125": (power_law_weighted_instance, {"beta": 0.125}),
    "log": (log_weighted_instance, {}),
    "optimal-macro-recall-test-marginals": (optimal_macro_recall, {}),
    "optimal-macro-recall": (optimal_macro_recall, {}),

    # Block coordinate with default paramters - commented out because it better to use variatns with specific tolerance to stoping condition
    # "block-coord-macro-prec": (block_coordinate_macro_precision, {}),
    # "block-coord-macro-recall": (block_coordinate_macro_recall, {}),
    # "block-coord-macro-f1": (block_coordinate_macro_f1, {}),
    
    # Mixed precision
    "block-coord-mixed-prec-prec-alpha=0.1-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.1, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.03162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.03162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.01-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.01, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.0003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.0001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.00003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.00001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.000003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.000003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.000001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.000001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.0000003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0000003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.0000001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0000001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.00000003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00000003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-prec-alpha=0.00000001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00000001, "tolerance": 1e-7}),

    # Greedy mixed precision 
    # "greedy-mixed-prec-prec-alpha=0.01": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.01, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.003162": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.001": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.0003162": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.0001": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.00003162": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.00001": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.00001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.000003162": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.000003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.000001": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.000001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.0000003162": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0000003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-prec-alpha=0.0000001": (block_coordinate_mixed_instance_prec_macro_prec,{"alpha": 0.0000001, "greedy_start": True, "max_iter": 1}),
   
    # Mixed precision with macro f1
    "block-coord-mixed-prec-f1-alpha=0.01-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.01, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.0003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.0001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.00003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.00003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.00001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.00001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.000003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.000003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.000001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.000001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.0000003162-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0000003162, "tolerance": 1e-7}),
    "block-coord-mixed-prec-f1-alpha=0.0000001-tol=1e-7": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0000001, "tolerance": 1e-7}),

    # Greedy mixed precision with macro f1
    # "greedy-mixed-prec-f1-alpha=0.01": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.01, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.003162": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.001": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.0003162": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.0001": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.00003162": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.00003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.00001": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.00001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.000003162": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.000003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.000001": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.000001, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.0000003162": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0000003162, "greedy_start": True, "max_iter": 1}),
    # "greedy-mixed-prec-f1-alpha=0.0000001": (block_coordinate_mixed_instance_prec_macro_f1,{"alpha": 0.0000001, "greedy_start": True, "max_iter": 1}),
    
    # Greedy
    "greedy-macro-prec": (block_coordinate_macro_precision, {"greedy_start": True, "max_iter": 1}),
    "greedy-macro-recall": (block_coordinate_macro_precision, {"greedy_start": True, "max_iter": 1}),
    "greedy-macro-f1": (block_coordinate_macro_f1, {"greedy_start": True, "max_iter": 1}),
    "block-coord-macro-prec-iter=1": (block_coordinate_macro_precision, {"max_iter": 1}),
    #"block-coord-macro-recall-iter=1": (block_coordinate_macro_precision, {"max_iter": 1}),
    "block-coord-macro-f1-iter=1": (block_coordinate_macro_f1, {"max_iter": 1}),
    # "greedy-start-block-coord-macro-prec": (block_coordinate_macro_precision, {"greedy_start": True}),
    # "greedy-start-block-coord-macro-recall": (block_coordinate_macro_f1, {"greedy_start": True}),
    # "greedy-start-block-coord-macro-f1": (block_coordinate_macro_f1, {"greedy_start": True}),

    # Coverage
    "block-coord-cov": (block_coordinate_coverage, {}),
    "greedy-cov": (block_coordinate_coverage, {"greedy_start": True, "max_iter": 1}),
    "block-coord-cov-iter=1": (block_coordinate_coverage, {"max_iter": 1}),
    # "greedy-start-block-coord-cov": (block_coordinate_coverage, {"greedy_start": True}),
    
    # Tolerance on stopping condiction experiments
    #"block-coord-macro-prec-tol=1e-1": (block_coordinate_macro_precision, {"tolerance": 1e-1}),
    #"block-coord-macro-prec-tol=1e-2": (block_coordinate_macro_precision, {"tolerance": 1e-2}),
    "block-coord-macro-prec-tol=1e-3": (block_coordinate_macro_precision, {"tolerance": 1e-3}),
    "block-coord-macro-prec-tol=1e-4": (block_coordinate_macro_precision, {"tolerance": 1e-4}),
    "block-coord-macro-prec-tol=1e-5": (block_coordinate_macro_precision,{"tolerance": 1e-5}),
    "block-coord-macro-prec-tol=1e-6": (block_coordinate_macro_precision,{"tolerance": 1e-6}),
    "block-coord-macro-prec-tol=1e-7": (block_coordinate_macro_precision,{"tolerance": 1e-7}),
    #"block-coord-macro-prec-tol=1e-8": (block_coordinate_macro_precision,{"tolerance": 1e-8}),
    
    #"block-coord-macro-recall-tol=1e-3": (block_coordinate_macro_recall,{"tolerance": 1e-3}),
    "block-coord-macro-recall-tol=1e-4": (block_coordinate_macro_recall,{"tolerance": 1e-4}),
    "block-coord-macro-recall-tol=1e-5": (block_coordinate_macro_recall,{"tolerance": 1e-5}),
    "block-coord-macro-recall-tol=1e-6": (block_coordinate_macro_recall,{"tolerance": 1e-6}),
    "block-coord-macro-recall-tol=1e-7": (block_coordinate_macro_recall,{"tolerance": 1e-7}),
    #"block-coord-macro-recall-tol=1e-8": (block_coordinate_macro_recall,{"tolerance": 1e-8}),
    
    #"block-coord-macro-f1-tol=1e-1": (block_coordinate_macro_f1,{"tolerance": 1e-1}),
    #"block-coord-macro-f1-tol=1e-2": (block_coordinate_macro_f1,{"tolerance": 1e-2}),
    "block-coord-macro-f1-tol=1e-3": (block_coordinate_macro_f1,{"tolerance": 1e-3}),
    "block-coord-macro-f1-tol=1e-4": (block_coordinate_macro_f1,{"tolerance": 1e-4}),
    "block-coord-macro-f1-tol=1e-5": (block_coordinate_macro_f1,{"tolerance": 1e-5}),
    "block-coord-macro-f1-tol=1e-6": (block_coordinate_macro_f1,{"tolerance": 1e-6}),
    "block-coord-macro-f1-tol=1e-7": (block_coordinate_macro_f1,{"tolerance": 1e-7}),
    #"block-coord-macro-f1-tol=1e-8": (block_coordinate_macro_f1,{"tolerance": 1e-8}),
    

    #"block-coord-cov-tol=1e-1": (block_coordinate_coverage,{"tolerance": 1e-1}),
    #"block-coord-cov-tol=1e-2": (block_coordinate_coverage,{"tolerance": 1e-2}),
    "block-coord-cov-tol=1e-3": (block_coordinate_coverage,{"tolerance": 1e-3}),
    "block-coord-cov-tol=1e-4": (block_coordinate_coverage,{"tolerance": 1e-4}),
    "block-coord-cov-tol=1e-5": (block_coordinate_coverage,{"tolerance": 1e-5}),
    "block-coord-cov-tol=1e-6": (block_coordinate_coverage,{"tolerance": 1e-6}),
    "block-coord-cov-tol=1e-7": (block_coordinate_coverage,{"tolerance": 1e-7}),
    #"block-coord-cov-tol=1e-8": (block_coordinate_coverage,{"tolerance": 1e-8}),

    # Mixed precision with cov
    "block-coord-mixed-prec-cov-alpha=0.001-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.001, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.01-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.01, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.05-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.05, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.1-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.1, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.2-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.2, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.3-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.3, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.4-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.4, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.5-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.5, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.6-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.6, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.7-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.7, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.8-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.8, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.9-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.9, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.95-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.95, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.99-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.99, "tolerance": 1e-7}),
    "block-coord-mixed-prec-cov-alpha=0.999-tol=1e-7": (block_coordinate_coverage,{"alpha": 0.999, "tolerance": 1e-7}),
}


def report_metrics(data, predictions, k):
    results = {}
    for metric, func in METRICS.items():
        value = func(data, predictions)
        results[f"{metric}@{k}"] = value
        print(f"  {metric}: {100 * value:>5.2f}")

    return results


@click.command()
@click.argument("experiment", type=str, required=True)
@click.option("-k", type=int, required=False, default=None)
@click.option("-s", "--seed", type=int, required=False, default=None)
def main(experiment, k, seed):
    print(experiment)

    if k is not None:
        K = (k,)

    true_as_pred = "true_as_pred" in experiment
    lightxml_data = "lightxml" in experiment

    plt_loss = "log"

    lightxml_data_load_config = {
        "labels_delimiter": " ",
        "labels_features_delimiter": None,
        "header": False,
    }
    xmlc_data_load_config = {
        "labels_delimiter": ",",
        "labels_features_delimiter": " ",
        "header": True,
    }

    if "yeast_plt" in experiment:
        # yeast - PLT
        xmlc_data_load_config["header"] = False
        eta_pred_path = {
            "path": f"predictions/yeast_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/yeast/yeast_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/yeast/yeast_train.txt",
            "load_func": load_txt_labels,
        }

    elif "youtube_deepwalk_plt" in experiment:
        xmlc_data_load_config["header"] = False
        eta_pred_path = {
            "path": f"predictions/youtube_deepwalk_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/youtube_deepwalk/youtube_deepwalk_test.svm",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/youtube_deepwalk/youtube_deepwalk_train.svm",
            "load_func": load_txt_labels,
        }

    elif "eurlex_lexglue_plt" in experiment:
        xmlc_data_load_config["header"] = False
        eta_pred_path = {
            "path": f"predictions/eurlex_lexglue_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/eurlex_lexglue/eurlex_lexglue_test.svm",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/eurlex_lexglue/eurlex_lexglue_train.svm",
            "load_func": load_txt_labels,
        }

    elif "mediamill_plt" in experiment:
        # mediamill - PLT
        xmlc_data_load_config["header"] = False
        eta_pred_path = {
            "path": f"predictions/mediamill_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/mediamill/mediamill_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/mediamill/mediamill_train.txt",
            "load_func": load_txt_labels,
        }

    elif "flicker_deepwalk_plt" in experiment:
        xmlc_data_load_config["header"] = False
        eta_pred_path = {
            "path": f"predictions/flicker_deepwalk_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/flicker_deepwalk/flicker_deepwalk_test.svm",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/flicker_deepwalk/flicker_deepwalk_train.svm",
            "load_func": load_txt_labels,
        }

    elif "rcv1x_plt" in experiment:
        # RCV1X - PLT + XMLC repo data
        eta_pred_path = {
            "path": f"predictions/rcv1x_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/rcv1x/rcv1x_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/rcv1x/rcv1x_train.txt",
            "load_func": load_txt_labels,
        }

    elif "eurlex_plt" in experiment:
        # Eurlex - PLT + XMLC repo data
        eta_pred_path = {
            "path": f"predictions/eurlex_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/eurlex/eurlex_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/eurlex/eurlex_train.txt",
            "load_func": load_txt_labels,
        }

    elif "amazoncat_plt" in experiment:
        # AmazonCat - PLT + XMLC repo data
        eta_pred_path = {
            "path": f"predictions/amazonCat_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/amazonCat/amazonCat_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/amazonCat/amazonCat_train.txt",
            "load_func": load_txt_labels,
        }

    elif "wiki10_plt" in experiment:
        # Wiki10 - PLT + XMLC repo data
        eta_pred_path = {
            "path": f"predictions/wiki10_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/wiki10/wiki10_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/wiki10/wiki10_train.txt",
            "load_func": load_txt_labels,
        }

    elif "amazon_plt" in experiment:
        # Amazon - PLT + XMLC repo data
        eta_pred_path = {
            "path": f"predictions/amazon_top_200_{plt_loss}",
            "load_func": load_txt_sparse_pred,
        }
        y_true_path = {
            "path": "datasets/amazon/amazon_test.txt",
            "load_func": load_txt_labels,
        }
        train_y_true_path = {
            "path": "datasets/amazon/amazon_train.txt",
            "load_func": load_txt_labels,
        }

    elif "eurlex_lightxml" in experiment:
        # Eurlex - LightXML
        y_true_path = {
            "path": "datasets/EUR-Lex/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/eurlex/eurlex4k_full_plain-scores.npy",
            "load_func": load_npy_full_pred,
            "keep_top_k": 100,
            "apply_sigmoid": True,
        }
        train_y_true_path = {
            "path": "datasets/EUR-Lex/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "amazoncat_lightxml" in experiment:
        # Wiki - LightXML
        y_true_path = {
            "path": "datasets/AmazonCat-13K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/amazonCat_top_100.notnpz",
            "load_func": load_npz_wrapper,
            "apply_sigmoid": True,
        }
        train_y_true_path = {
            "path": "datasets/AmazonCat-13K/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "wiki10_lightxml" in experiment:
        # Wiki - LightXML
        y_true_path = {
            "path": "datasets/Wiki10-31K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/wiki10_top_100.notnpz",
            "load_func": load_npz_wrapper,
            "apply_sigmoid": True,
        }
        train_y_true_path = {
            "path": "datasets/Wiki10-31K/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "amazon_lightxml" in experiment:
        # Amazon - LightXML
        y_true_path = {
            "path": "datasets/Amazon-670K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/amazon/amazon670k_light_t0",
            "load_func": load_npy_sparse_pred,
        }
        train_y_true_path = {
            "path": "datasets/Amazon-670K/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "amazon_1000_lightxml" in experiment:
        # Amazon - LightXML
        y_true_path = {
            "path": "datasets/Amazon-670K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/amazon_1000/amazon670k_light_original_t0",
            "load_func": load_npy_sparse_pred,
        }
        train_y_true_path = {
            "path": "datasets/Amazon-670K/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "wiki500_lightxml" in experiment:
        # WikiLarge - LightXML
        y_true_path = {
            "path": "datasets/Wiki-500K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/wiki500/wiki500k_light_t0",
            "load_func": load_npy_sparse_pred,
        }
        train_y_true_path = {
            "path": "datasets/Wiki-500K/train_labels.txt",
            "load_func": load_txt_labels,
        }

    elif "wiki500_1000_lightxml" in experiment:
        # WikiLarge - LightXML
        y_true_path = {
            "path": "datasets/Wiki-500K/test_labels.txt",
            "load_func": load_txt_labels,
        }
        eta_pred_path = {
            "path": "predictions/wiki500_1000/wiki500k_light_original_t0",
            "load_func": load_npy_sparse_pred,
        }
        train_y_true_path = {
            "path": "datasets/Wiki-500K/train_labels.txt",
            "load_func": load_txt_labels,
        }
    
    else:
        raise RuntimeError(f"No matching experiment: {experiment}")

    # Remap labels for LightXML predictions and use it when loading data
    if lightxml_data:
        with Timer():
            labels_map = calculate_lightxml_labels(
                train_y_true_path["path"], y_true_path["path"]
            )
        train_y_true_path.update(lightxml_data_load_config)
        y_true_path.update(lightxml_data_load_config)
        train_y_true_path["labels_map"] = labels_map
        y_true_path["labels_map"] = labels_map
    else:
        train_y_true_path.update(xmlc_data_load_config)
        y_true_path.update(xmlc_data_load_config)

    # Create binary files for faster loading
    with Timer():
        y_true = load_cache_npz_file(**y_true_path)

    with Timer():
        eta_pred = load_cache_npz_file(**eta_pred_path)

    with Timer():
        train_y_true = load_cache_npz_file(**train_y_true_path)

    # For some sparse format this resize might be necessary
    if y_true.shape != eta_pred.shape:
        if y_true.shape[0] != eta_pred.shape[0]:
            raise RuntimeError(
                f"Number of instances in true and prediction do not match {y_true.shape[0]} != {eta_pred.shape[0]}"
            )
        align_dim1(y_true, eta_pred)

    # Calculate marginals and propensities
    with Timer():
        print("Calculating marginals and propensities")
        marginals = labels_priors(train_y_true)
        # marginals = labels_priors(y_true)
        inv_ps = jpv_inverse_propensity(train_y_true)

    if "apply_sigmoid" in eta_pred_path and eta_pred_path["apply_sigmoid"]:
        # LightXML predictions aren't probabilities
        eta_pred.data = 1.0 / (1.0 + np.exp(-eta_pred.data))

    # Use true labels as predictions with 1.0 score (probability)
    if true_as_pred:
        eta_pred = y_true

    print(f"y_true: type={type(y_true)}, shape={y_true.shape}")
    print(f"eta_pred: type={type(eta_pred)}, shape={eta_pred.shape}")

    # Convert to array to check if it gives the same results
    # y_true = y_true.toarray()
    # eta_pred = eta_pred.toarray()

    # This does not work at the moment, since original dense code was writeen
    # y_true = y_true.todense() # As np.matrix
    # eta_pred = eta_pred.todense() # As np.matrix

    output_path_prefix = f"results_bca/{experiment}/"
    os.makedirs(output_path_prefix, exist_ok=True)
    for k in K:
        for method, func in METHODS.items():
            print(f"{experiment} - {method} @ {k}: ")

            output_path = f"{output_path_prefix}{method}_k={k}_s={seed}"
            results_path = f"{output_path}_results.json"
            pred_path = f"{output_path}_pred.npz"

            if not os.path.exists(results_path) or RECALCULATE_RESUTLS:
                results = {}
                if not os.path.exists(pred_path) or RECALCULATE_PREDICTION:
                    with Timer() as t:
                        # y_pred = func[0](eta_pred, k, marginals=marginals, inv_ps=inv_ps, filename=output_path, **func[1])
                        y_pred, meta = func[0](
                            eta_pred,
                            k,
                            marginals=marginals,
                            inv_ps=inv_ps,
                            seed=seed,
                            **func[1],
                        )
                        results["iters"] = meta["iters"]
                        results["time"] = t.get_time()
                        print("  Iters: ", meta["iters"])
                    save_npz_wrapper(pred_path, y_pred)
                    save_json(results_path, results)
                else:
                    y_pred = load_npz_wrapper(pred_path)
                    results = load_json(results_path)

                print("  Calculating metrics:")
                results.update(report_metrics(y_true, y_pred, k))
                save_json(results_path, results)

            print("  Done")


if __name__ == "__main__":
    main()
