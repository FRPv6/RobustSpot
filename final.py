import copy

import mining
import config.global_data as g_data


def get_merge_res(top5_3iter):
    # 将不同迭代的同维度的根因合并计算PS值
    merge_causes = []
    merge_causes += get_merge_causes_2(top5_3iter, 0, 1)
    merge_causes += get_merge_causes_2(top5_3iter, 0, 2)
    merge_causes += get_merge_causes_2(top5_3iter, 1, 2)
    merge_causes += get_merge_cause_3(top5_3iter)  # 是否考虑三个 并列根因的情况
    return merge_causes


def get_merge_causes_2(top5_3iter, first, second):
    merge_causes = []
    for cause1 in top5_3iter[first]:
        for cause2 in top5_3iter[second]:
            if len(cause1) == len(cause2):
                flag_same_column = True
                flag_diff_value = False
                for cause_index in range(len(cause1)):
                    if cause1[cause_index][0] != cause2[cause_index][0]:  # 属性名称不相同
                        flag_same_column = False
                    if cause1[cause_index][1] != cause2[cause_index][1]:  # 存在一个属性不相同的值
                        flag_diff_value = True
                if flag_same_column and flag_diff_value:  # 属性名称不相同 且 存在一个属性不相同的值
                    merge_causes.append([cause1, cause2])
    return merge_causes


def get_merge_cause_3(top5_3iter):
    merge_causes = []
    for cause1 in top5_3iter[0]:
        for cause2 in top5_3iter[1]:
            for cause3 in top5_3iter[2]:
                if len(cause1) == len(cause2) and len(cause2) == len(cause3):
                    flag_same_column = True
                    flag_diff_value = False
                    for cause_index in range(len(cause1)):
                        if not (cause1[cause_index][0] == cause2[cause_index][0]
                                and cause1[cause_index][0] == cause3[cause_index][0]):  # 属性名称有一个不相同
                            flag_same_column = False
                        if cause1[cause_index][1] != cause2[cause_index][1] and \
                                cause1[cause_index][1] != cause3[cause_index][1] and \
                                cause2[cause_index][1] != cause3[cause_index][1]:  # 存在一个 三个的属性都不同的值
                            flag_diff_value = True
                    if flag_same_column and flag_diff_value:  # 属性名称不相同 且 存在一个属性不相同的值
                        merge_causes.append([cause1, cause2, cause3])
    return merge_causes


def merge_larger_dimension(merge_res, index):
    # 多跟因时，出现结果中同一维度的结果占据整个根因对应的叶子节点在预测数据表钟的大部分比例，
    # 这时，将这一维度去掉，将其他维度合并为多跟因。
    # 找到在多跟因中值相同的维度
    merge_cause = merge_res[index]
    record_dict = dict()
    for merge_cause_item in merge_cause:
        for item in merge_cause_item:
            if item[0] in record_dict.keys():
                if item[1] not in record_dict[item[0]]:
                    record_dict[item[0]].append(item[1])
            else:
                record_dict[item[0]] = [item[1]]
    # record_dict的values中长度为1的就是对应值相同的维度
    keep_items = []
    for k, v in record_dict.items():
        if len(v) == 1:
            keep_items.append((k, v[0]))
    # 将值相同的维度去掉， 分别算出去掉前后的根因对应的叶子结点在筛选前表中支持度，求出去掉前/去掉后
    # 去掉前
    if len(keep_items) > 0:
        before_support = mining.get_support(merge_cause, g_data.before_df_list[0])
        # copy_merge_cause = [copy.deepcopy(list(item)) for item in merge_cause]
        # for merge_cause_item in copy_merge_cause:
        #     for item in keep_items:
        #         merge_cause_item.remove(item)
        # copy_merge_cause = [tuple(item) for item in copy_merge_cause]
        after_support = mining.get_support(tuple(keep_items), g_data.before_df_list[0])

        if before_support / after_support >= 0.9:
            # print('-' * 100)
            # print('record_dict:', record_dict)
            # print('keep_items:', keep_items)
            # print('merge_cause:', merge_cause)
            # # print('copy_merge_cause:', copy_merge_cause)
            # print('before_support / after_support = ', before_support / after_support)
            # print('-' * 100)
            merge_res[index] = [tuple(keep_items)]
