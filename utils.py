import datetime
import random
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

import torch
from torch_geometric.utils import add_remaining_self_loops


def set_random_seed(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)


def get_date_postfix():
    dt = datetime.datetime.now()
    post_fix = '{}_{:02d}-{:02d}-{:02d}'.format(dt.date(), dt.hour, dt.minute, dt.second)
    return post_fix


def get_n_params(model):
    pp = 0
    for p in list(model.parameters()):
        nn = 1
        for s in list(p.size()):
            nn = nn * s
        pp += nn
    return pp


def set_logger(my_str):
    task_time = get_date_postfix()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    Path(f"log/").mkdir(parents=True, exist_ok=True)
    logger_name = f"{my_str}_{task_time}.log"
    fh = logging.FileHandler(f"log/{logger_name}")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def get_degree(edge_index):
    s = pd.Series(edge_index.view(-1).numpy())
    return s.value_counts().sort_index().values


def get_norm_degree(metapath_data, num_relations):
    norm_degrees = []
    for i in range(num_relations):
        degree = get_degree(metapath_data[f'metapath_{i}'].edge_index)
        norm_degree = MinMaxScaler(feature_range=(-1, 1)).fit_transform(degree.reshape(-1, 1))
        norm_degrees.append(norm_degree)
    norm_degrees = torch.from_numpy(np.stack(norm_degrees).squeeze(-1))
    return norm_degrees


def add_self_loop(metapath_data, num_relations, num_nodes):
    for i in range(num_relations):
        new_edge_index, _ = add_remaining_self_loops(metapath_data[f'metapath_{i}'].edge_index, fill_value=1, num_nodes=num_nodes)
        metapath_data[f'metapath_{i}'].edge_index = new_edge_index
    return metapath_data
