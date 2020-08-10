from kneed import KneeLocator
import pandas as pd
from functools import reduce
from operator import and_

import config.global_data as g_data
import predict
import ID_CA


def drop_last_top(df, last_dig_root_cause):
    def get_all_mask(value):
        def single_mask(v):
            # v: (column, value)
            column = v[0]  # 列名
            return df[column] == v[1]  # mask

        mask = reduce(and_, map(single_mask, value))
        return mask
    return df[~get_all_mask(last_dig_root_cause)]


def select_expand(dim1, dim2, anomaly_index):
    before_df = None
    after_df = None
    expand_df = None
    index = None
    if dim1 == 0 and dim2 == 0:
        # 筛选前的数据从数据文件的预测中获取
        before_df = predict.get_predict_df(anomaly_index)
        g_data.row_num = before_df.shape[0]  # 预测表的行数
        index = 0
    else:
        index = 2 * dim1 + dim2 - 2
        if dim2 == 1:
            # 恢复(删除)[0][0]次迭代的top[dim1]
            before_df = drop_last_top(g_data.before_df_list[0], g_data.dig_root_cause[0][dim1-1])
        else:
            # 恢复(删除)[dim1][dim2-1]次迭代的top[0]
            before_df = drop_last_top(g_data.before_df_list[index-1], g_data.dig_root_cause[index-1][0])
    # before_df.reset_index(inplace=True)
    # 计算influence_degree和contribution_ability
    before_df = ID_CA.get_influence_degree(before_df)
    before_df = ID_CA.get_contribution_ability(before_df)
    # 按照ID和CA筛选
    influence_degree_threshold = 0.5
    contribution_ability_threshold = 0
    # 采用拐点的方法获取influence_degree的阈值
    influence_degree_list = before_df['ID'].values.tolist()
    if influence_degree_list:
        influence_degree_list.sort()
        influence_degree_list = list(filter(lambda x: x > 0, influence_degree_list))

        def get_cdf():
            cdf_list = [0] * len(influence_degree_list)
            for i in range(len(influence_degree_list)):
                cdf_list[i] = (i + 1) / len(influence_degree_list)
            return cdf_list

        influence_degree_cdf = get_cdf()

        try:
            knee_concave = KneeLocator(influence_degree_list, influence_degree_cdf, S=6,
                                       interp_method='polynomial', curve='concave', direction='increasing').knee
            knee = knee_concave
            if knee is None:
                pass
            else:
                influence_degree_threshold = knee
        except:
            pass
    # 按照阈值筛选
    after_df = before_df[
        (before_df['ID'] > influence_degree_threshold)
        &
        (before_df['CA'] > contribution_ability_threshold)
    ]
    # after_df.reset_index(inplace=True)
    before_df = before_df.drop(columns=['ID', 'CA'])
    # 按照ID和CA的乘积的100倍扩展表的每一行
    attribute_columns = g_data.anomaly_list[anomaly_index]['header']
    expand_list = []
    for _, row in after_df.iterrows():
        expand_times = int(row['ID'] * row['CA'] * 100)
        expand_list.extend([dict(row[attribute_columns])] * expand_times)
    expand_df = pd.DataFrame(expand_list)
    # 将三种表分别存在全局变量中
    g_data.before_df_list[index] = before_df
    g_data.after_df_list[index] = after_df
    g_data.expand_df_list[index] = expand_df
    return index

