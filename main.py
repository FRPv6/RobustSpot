import numpy as np
import yaml
import copy
import warnings

import config.global_data as g_data
import final
import mining
import select_expand


def cause_mining(dim1, dim2, anomaly_index):
    iter_index = select_expand.select_expand(dim1, dim2, anomaly_index)
    mining.mining(iter_index)

def main():
    anomaly_config = open(g_data.anomaly_config, mode='r', encoding='utf-8')
    g_data.anomaly_list = yaml.load(anomaly_config.read(), Loader=yaml.FullLoader)
    for anomaly_index in range(len(g_data.anomaly_list)):
        cause_mining(0, 0, anomaly_index)
        cause_mining(1, 1, anomaly_index)
        if g_data.mining_root_cause[1]:
            cause_mining(1, 2, anomaly_index)
        else:
            g_data.mining_root_cause[2] = []
        cause_mining(2, 1, anomaly_index)
        if g_data.mining_root_cause[3]:
            cause_mining(2, 2, anomaly_index)
        else:
            g_data.mining_root_cause[4] = []
        cause_mining(3, 1, anomaly_index)
        if g_data.mining_root_cause[5]:
            cause_mining(3, 2, anomaly_index)
        else:
            g_data.mining_root_cause[6] = []

        merge_res = []
        merge_res += final.get_merge_res(
            [g_data.mining_root_cause[0][:1], g_data.mining_root_cause[1][:1], g_data.mining_root_cause[2]])
        merge_res += final.get_merge_res(
            [g_data.mining_root_cause[0][1:2], g_data.mining_root_cause[3][:1], g_data.mining_root_cause[4]])
        merge_res += final.get_merge_res(
            [g_data.mining_root_cause[0][2:3], g_data.mining_root_cause[5][:1], g_data.mining_root_cause[6]])
        merge_res += [[item] for item in g_data.mining_root_cause[0]]
        for index in range(len(merge_res)):
            if len(merge_res[index]) == 2:
                copy_item = [copy.deepcopy(set(merge_res[index][0])), copy.deepcopy(set(merge_res[index][1]))]
                copy_item[0].discard(('p2p', 1))
                copy_item[0].discard(('p2p', 0))
                copy_item[1].discard(('p2p', 1))
                copy_item[1].discard(('p2p', 0))
                if copy_item[0] == copy_item[1] and copy_item[0]:
                    merge_res[index] = [tuple(copy_item[0])]
        for index in range(len(merge_res)):
            if len(merge_res[index]) > 1:
                final.merge_larger_dimension(merge_res, index)
        merge_res_set_list = [set(item) for item in merge_res]
        merge_res_new = []
        for item in merge_res_set_list:
            if item not in merge_res_new:
                merge_res_new.append(item)
        merge_res = [list(item) for item in merge_res_new]
        support_delta = [
            mining.get_support(item, g_data.before_df_list[0]) - mining.get_support(item, g_data.after_df_list[0])
            for item in merge_res
        ]
        support_delta = np.array(support_delta)
        sorted_index = np.argsort(support_delta)[:5]
        final_root_cause = []
        for index in sorted_index:
            final_root_cause.append(merge_res[index])
        g_data.final_res.append(final_root_cause)
        g_data.before_df_list = [None] * 7
        g_data.after_df_list = [None] * 7
        g_data.expand_df_list = [None] * 7
        g_data.mining_root_cause = [None] * 7
        g_data.col_num = len(g_data.anomaly_list[anomaly_index]['header'])
        g_data.final_res.loc[g_data.anomaly_list[anomaly_index]['data']] = [final_root_cause]
        print(f'{g_data.anomaly_list[anomaly_index]["data"]}')
    g_data.final_res.to_csv('result/result.csv')


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    main()
