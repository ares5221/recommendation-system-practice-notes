#!/usr/bin/env python
# encoding: utf-8
"""
@author: HuRuiFeng
@file: tc_itemcf.py
@time: 2020/5/7 10:10
@project: recommendation-system-practice-notes
@desc: 时间上下文相关的ItemCF算法
"""
import math
import time


class TCItemCF:
    def __init__(self, dataset, alpha=1.0, beta=1.0, t0=int(time.time())):
        """
        :param dataset: 训练数据集
        :param alpha: 计算item相似度的时间衰减因子
        :param beta: 推荐打分时的时间衰减因子
        :param t0: 当前的时间戳
        """
        self.sim = {}
        self.sorted_item_sim = {}
        self.dataset = dataset
        self.alpha = alpha
        self.beta = beta
        self.t0 = t0

    def fit(self):
        # 计算物品相似度矩阵
        sim = {}
        num = {}
        for user in self.dataset:
            items = self.dataset[user]
            for i in range(len(items)):
                u, t1 = items[i]
                if u not in num:
                    num[u] = 0
                num[u] += 1
                if u not in sim:
                    sim[u] = {}
                for j in range(len(items)):
                    if j == i:
                        continue
                    v, t2 = items[j]
                    if v not in sim[u]:
                        sim[u][v] = 0
                    sim[u][v] += 1.0 / (self.alpha * (abs(t1 - t2) + 1))
        for u in sim:
            for v in sim[u]:
                sim[u][v] /= math.sqrt(num[u] * num[v])

        self.sim = sim
        # 按照相似度排序
        self.sorted_item_sim = {k: list(sorted(v.items(), key=lambda x: x[1], reverse=True))
                                for k, v in sim.items()}

    def recommend_users(self, users, N, K=None):
        """
        给用户推荐的商品
        :param users: 用户
        :param K: 不需要，为了统一调用
        :param N: 超参数，设置取TopN推荐物品数目
        :return: 推荐字典 {用户 : 推荐的商品的list}
        """
        recommend_items = dict()
        for user in users:
            user_recommends = self.recommend(user, N, K)
            recommend_items[user] = user_recommends

        return recommend_items

    def recommend(self, user, N, K):
        items = {}
        user_items = set()
        for item, _ in self.dataset[user]:
            user_items.add(item)

        for item, t in self.dataset[user]:
            for u, _ in self.sorted_item_sim[item][:K]:
                if u not in user_items:
                    if u not in items:
                        items[u] = 0
                    items[u] += self.sim[item][u] / (1 + self.beta * (self.t0 - t))
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        recs = [x[0] for x in recs]
        return recs
