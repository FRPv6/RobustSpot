'''
一次迭代的全过程，
需要传入两个变量区分哪次迭代。
包括获取筛选前的数据
计算影响度和贡献能力并筛选
扩展表
挖掘关联规则
推荐根因
'''

import select_expand
import mining


def dig_root(dim1, dim2, anomaly_index):
    iter_index = select_expand.select_expand(dim1, dim2, anomaly_index)
    mining.mining(dim1, dim2, anomaly_index, iter_index)
