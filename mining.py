import numpy as np
import itertools
from functools import reduce
from operator import and_

import config.global_data as g_data


def get_frequent_item_sets(df):
    frequent_item_sets = []
    for item in {column: df[column].mode() for column in df.columns}.items():
        frequent_item_sets.append((item[0], item[1].values[0]))
    return frequent_item_sets


def get_power_set(iterable, down_len, up_len):
    '''
    powerset([1,2,3]) --> (1,2) (1,3) (2,3) (1,2,3)
    生成幂集元素个数为2个或者3个
    '''
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(down_len, up_len))


def get_split_set(iterable):
    """
    split([1, 2, 3]) -->
    ((1,), (2, 3)), ((2,), (1, 3)), ((3,), (1, 2)),
    ((1, 2), (3,)), ((1, 3), (2,)), ((2, 3,), (1,))"
    """
    s = list(iterable)
    sets = set(s)
    res = []
    for r in range(1, len(s)):
        for lhs in itertools.combinations(s, r):
            rhs = tuple(sets - set(lhs))
            rule = (lhs, rhs)  # tuple
            res.append(rule)
    return res


def get_support(root_cause, expand_df):

    def get_all_mask(value):
        def single_mask(v):
            # v: (column, value)
            column = v[0]  # 列名
            return expand_df[column] == v[1]  # mask

        mask = reduce(and_, map(single_mask, value))
        return mask

    def get_num(value):
        return len(expand_df[get_all_mask(value)])

    if isinstance(root_cause, list):
        total_num = 0
        for item in root_cause:
            total_num += get_num(item)
        return total_num / expand_df.shape[0]
    else:
        return get_num(root_cause) / expand_df.shape[0]


def count_confidence(expand_df, rule):
    lhs, rhs = rule

    def get_all_mask(value):
        def single_mask(v):
            # v: (column, value)
            column = v[0]  # 列名
            return expand_df[column] == v[1]  # mask

        mask = reduce(and_, map(single_mask, value))
        return mask

    def get_num(value):
        return len(expand_df[get_all_mask(value)])

    num_left = get_num(lhs)
    if num_left == 0:
        return 0
    num_left_right = get_num(lhs + rhs)
    return num_left_right / num_left


def mining(dim1, dim2, anomaly_index, iter_index, confidence_threshold=0.8):
    expand_df = g_data.expand_df_list[iter_index]
    cross_root_cause = []
    root_cause = []
    # 获取各个维度的频繁项
    frequent_item_sets = get_frequent_item_sets(expand_df)
    # 获取频繁项对应的幂集列表
    power_set_list = list(get_power_set(frequent_item_sets, 2, 4))
    # 获取每个幂集对应的总的关联规则的集合
    rules = list(set(itertools.chain.from_iterable(map(get_split_set, power_set_list))))
    # 计算每一个关联规则的置信度，算出左边和右边交集的支持度，除以左边的支持度
    confidences = [count_confidence(expand_df, rule) for rule in rules]
    # 按照支持度的阈值筛选规则
    for confidence, rule in zip(confidences, rules):
        if confidence > confidence_threshold:
            cross_root_cause.append(rule[0] + rule[1])
    # 对root_cause去重
    cross_root_cause = [set(item) for item in cross_root_cause]
    for item in cross_root_cause:
        if item not in root_cause:
            root_cause.append(item)
    root_cause = [tuple(item) for item in root_cause]
    # 根因加上频繁项
    root_cause.extend(list(get_power_set(frequent_item_sets, 1, 2)))
    # 按照在筛选前的表和筛选后的表中的支持度的差值从小到大排序
    before_df = g_data.before_df_list[iter_index]
    after_df = g_data.after_df_list[iter_index]
    # 计算支持度的差值
    support_delta = [
        get_support(root_cause_item, before_df) - get_support(root_cause_item, after_df)
        for root_cause_item in root_cause
    ]
    support_delta = np.array(support_delta)
    sorted_index = np.argsort(support_delta)[:5]  # 取前5个
    # 一次dig_root迭代推荐的5个根因
    dig_root_cause = []
    for index in sorted_index:
        # 将多维度的根因，按照属性名排序
        root_cause_list = list(root_cause[index])
        root_cause_list.sort(key=lambda item: item[0])
        dig_root_cause.append(tuple(root_cause_list))
    # 修改全局变量的dig_root_cause[iter_index]
    g_data.dig_root_cause[iter_index] = dig_root_cause

