# -*- coding: utf-8 -*-

import pandas as pd
from scipy.spatial.distance import cdist

eml_emb_sim_threshold = 0.88
eml_emb_sim_cand_num = 5

chat_emb_sim_threshold = 0.89
chat_emb_sim_cand_num = 4

bot_emb_sim_threshold = 0.90
bot_emb_sim_cand_num = 3

kb_emb_sim_threshold = 0.91
kb_emb_sim_cand_num = 2

custom_emb_sim_threshold = 0.92
custom_emb_sim_cand_num = 1

spider_emb_sim_threshold = 0.93
spider_emb_sim_cand_num = 1


def gen_emb_context(query_emb, emb_csv, sim_threshold, emb_cand_num, content_col_name="content"):
    df_shop_chat_embs = pd.read_csv(emb_csv, encoding="utf-8")
    shop_chat_embs = df_shop_chat_embs["content_emb"].apply(lambda x: eval(x)).tolist()

    cosine_sims = 1 - cdist(query_emb, shop_chat_embs, 'cosine')
    df_shop_chat_embs["cosine_sim"] = cosine_sims[0]
    filtered_chats = df_shop_chat_embs[df_shop_chat_embs['cosine_sim'] >= sim_threshold]
    nearest_chats = filtered_chats.nlargest(emb_cand_num, 'cosine_sim')[content_col_name].values.tolist()
    return nearest_chats
