import numpy as np
import yaml
import pandas as pd
import datetime
import copy
import warnings


import config.global_data as g_data
import dig_root
import final
import mining


def main(group):
    # 加载数据
    # group = 'single_3'
    anomaly_config = open(g_data.anomaly_config, mode='r', encoding='utf-8')
    g_data.anomaly_list = yaml.load(anomaly_config.read(), Loader=yaml.FullLoader)[group]
    for anomaly_index in range(len(g_data.anomaly_list)):
        start_time = datetime.datetime.now()
        dig_root.dig_root(0, 0, anomaly_index)
        dig_root.dig_root(1, 1, anomaly_index)
        if g_data.dig_root_cause[1]:
            dig_root.dig_root(1, 2, anomaly_index)
        else:
            g_data.dig_root_cause[2] = []
        dig_root.dig_root(2, 1, anomaly_index)
        if g_data.dig_root_cause[3]:
            dig_root.dig_root(2, 2, anomaly_index)
        else:
            g_data.dig_root_cause[4] = []
        dig_root.dig_root(3, 1, anomaly_index)
        if g_data.dig_root_cause[5]:
            dig_root.dig_root(3, 2, anomaly_index)
        else:
            g_data.dig_root_cause[6] = []

        merge_res = []
        # # 合并七次迭代的结果并排序
        merge_res += final.get_merge_res(
            [g_data.dig_root_cause[0][:1], g_data.dig_root_cause[1][:1], g_data.dig_root_cause[2]])
        merge_res += final.get_merge_res(
            [g_data.dig_root_cause[0][1:2], g_data.dig_root_cause[3][:1], g_data.dig_root_cause[4]])
        merge_res += final.get_merge_res(
            [g_data.dig_root_cause[0][2:3], g_data.dig_root_cause[5][:1], g_data.dig_root_cause[6]])
        merge_res += [[item] for item in g_data.dig_root_cause[0]]  # 加入首次迭代推荐的5个单根因

        # for item in merge_res:
        #     print(item)

        # 处理p2p导致的问题
        for index in range(len(merge_res)):
            if len(merge_res[index]) == 2:
                copy_item = [copy.deepcopy(set(merge_res[index][0])), copy.deepcopy(set(merge_res[index][1]))]
                copy_item[0].discard(('p2p', 1))
                copy_item[0].discard(('p2p', 0))
                copy_item[1].discard(('p2p', 1))
                copy_item[1].discard(('p2p', 0))
                if copy_item[0] == copy_item[1] and copy_item[0]:
                    # print(copy_item[0], copy_item[1], merge_res[index], [tuple(copy_item[0])], '-'*10)
                    merge_res[index] = [tuple(copy_item[0])]
        # 多跟因时，出现结果中同一维度的结果占据整个根因对应的叶子节点在预测数据表钟的大部分比例，
        # 这时，将这一维度去掉，将其他维度合并为多跟因。
        for index in range(len(merge_res)):
            if len(merge_res[index]) > 1:
                final.merge_larger_dimension(merge_res, index)



        # 对merge_res去重
        merge_res_set_list = [set(item) for item in merge_res]
        merge_res_new = []
        for item in merge_res_set_list:
            if item not in merge_res_new:
                merge_res_new.append(item)
        merge_res = [list(item) for item in merge_res_new]
        # 将最终的根因按照筛选前后的两个表中的支持度的差值排序
        support_delta = [
            mining.get_support(item, g_data.before_df_list[0]) - mining.get_support(item, g_data.after_df_list[0])
            for item in merge_res
        ]
        support_delta = np.array(support_delta)
        sorted_index = np.argsort(support_delta)[:5]  # 取前5个
        # 得到最终的5个推荐根因
        final_root_cause = []
        for index in sorted_index:
            final_root_cause.append(merge_res[index])
            # print(final_root_cause[-1])
        # print('-'*100)
        g_data.final_res.append(final_root_cause)
        g_data.before_df_list = [None] * 7
        g_data.after_df_list = [None] * 7
        g_data.expand_df_list = [None] * 7
        g_data.dig_root_cause = [None] * 7
        end_time = datetime.datetime.now()
        g_data.col_num = len(g_data.anomaly_list[anomaly_index]['header'])
        g_data.final_res.loc[g_data.anomaly_list[anomaly_index]['data']] = [final_root_cause, g_data.anomaly_list[anomaly_index]['cause'],
                                               g_data.row_num, g_data.col_num, (end_time - start_time).total_seconds()]
        print(f'{g_data.anomaly_list[anomaly_index]["data"]}: 用时{end_time - start_time}')
    g_data.final_res.to_csv(f'result/result_{group}.csv')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    warnings.filterwarnings('ignore')
    start1_ = datetime.datetime.now()
    group = 'multi_2'
    main(group)
    end1_ = datetime.datetime.now()
    print('All case use time:', end1_ - start1_)
