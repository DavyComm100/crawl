# -*- coding: utf-8 -*-

import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter

from openai_helper import *

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    # length_function=len
)


def get_emb_with_cache(df_eml_his_emb, content4embs):
    # 批量调用 & 性能优化 & 节省money
    existing_embeddings = df_eml_his_emb[df_eml_his_emb["content4emb"].isin(content4embs)]["content_emb"].tolist()
    existing_content4embs = df_eml_his_emb[df_eml_his_emb["content4emb"].isin(content4embs)]["content4emb"].tolist()
    existing_content_emb_map = dict(zip(existing_content4embs, existing_embeddings))
    new_content4embs = list(set(content4embs) - set(existing_content4embs))

    if len(new_content4embs) > 0:
        new_embeddings = get_emb(new_content4embs)
        new_content_emb_map = dict(zip(new_content4embs, new_embeddings))
    else:
        new_content_emb_map = {}

    merged_dict = {**existing_content_emb_map, **new_content_emb_map}
    content_embs = [merged_dict.get(element) for element in content4embs]
    return content_embs


def process_eml_his_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        email_history_emb_csv = os.path.join(bot_path, EMAIL_HISTORY_EMB)
        if os.path.exists(email_history_emb_csv):
            df_eml_his_emb = pd.read_csv(email_history_emb_csv, encoding="utf-8")
        else:
            df_eml_his_emb = pd.DataFrame({"content4emb": [], "content": [], "content_emb": []})

        content4embs, email_histories = [], []
        with open(save_path, "r") as file:
            for line in file:
                json_obj = json.loads(line)
                content4emb, email_history = extract_email_history(json_obj)
                content4embs.append("\n".join(content4emb))
                email_histories.append("\n".join(email_history))

        content_embs = get_emb_with_cache(df_eml_his_emb, content4embs)
        df_eml_his_emb = pd.DataFrame({"content4emb": content4embs, "content": email_histories, "content_emb": content_embs})
        df_eml_his_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_eml_his_emb.to_csv(email_history_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_eml_his_data failed...")


def process_chat_his_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        chat_history_emb_csv = os.path.join(bot_path, CHAT_HISTORY_EMB)
        if os.path.exists(chat_history_emb_csv):
            df_chat_his_emb = pd.read_csv(chat_history_emb_csv, encoding="utf-8")
        else:
            df_chat_his_emb = pd.DataFrame({"content4emb": [], "content": [], "content_emb": []})

        content4embs, chat_histories = [], []
        with open(save_path, "r") as file:
            for line in file:
                json_obj = json.loads(line)
                content4emb, chat_history = extract_chat_history(json_obj)
                content4embs.append(content4emb)
                chat_histories.append(chat_history)

        content_embs = get_emb_with_cache(df_chat_his_emb, content4embs)
        df_chat_his_emb = pd.DataFrame({"content4emb": content4embs, "content": chat_histories, "content_emb": content_embs})
        df_chat_his_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_chat_his_emb.to_csv(chat_history_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_chat_his_data failed...")


def process_bot_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        bot_emb_csv = os.path.join(bot_path, BOT_EMB)
        if os.path.exists(bot_emb_csv):
            df_bot_emb = pd.read_csv(bot_emb_csv, encoding="utf-8")
        else:
            df_bot_emb = pd.DataFrame({"content4emb": [], "content": [], "content_emb": []})

        content4embs, qas = [], []
        with open(save_path, "r") as file:
            for line in file:
                json_obj = json.loads(line)
                content4emb, qa = extract_qa(json_obj)
                content4embs.extend(content4emb)
                qas.extend(qa)

        content_embs = get_emb_with_cache(df_bot_emb, content4embs)
        df_bot_emb = pd.DataFrame({"content4emb": content4embs, "content": qas, "content_emb": content_embs})
        df_bot_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_bot_emb.to_csv(bot_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_bot_data failed...")


def process_kb_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        kb_emb_csv = os.path.join(bot_path, KB_EMB)
        if os.path.exists(kb_emb_csv):
            df_kb_emb = pd.read_csv(kb_emb_csv, encoding="utf-8")
        else:
            df_kb_emb = pd.DataFrame({"content4emb": [], "content": [], "content_emb": []})

        content4embs, qas = [], []
        with open(save_path, "r") as file:
            for line in file:
                json_obj = json.loads(line)
                content4emb, qa = extract_kb(json_obj)
                content4embs.extend(content4emb)
                qas.extend(qa)

        content_embs = get_emb_with_cache(df_kb_emb, content4embs)
        df_kb_emb = pd.DataFrame({"content4emb": content4embs, "content": qas, "content_emb": content_embs})
        df_kb_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_kb_emb.to_csv(kb_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_kb_data failed...")


def process_custom_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        custom_emb_csv = os.path.join(bot_path, CUSTOM_EMB)
        if os.path.exists(custom_emb_csv):
            df_custom_emb = pd.read_csv(custom_emb_csv, encoding="utf-8")
        else:
            df_custom_emb = pd.DataFrame({"content4emb": [], "content_emb": []})

        with open(save_path, "r") as file:
            text = file.read()
        docs = text_splitter.create_documents([text])
        content4embs = [doc.page_content for doc in docs]

        content_embs = get_emb_with_cache(df_custom_emb, content4embs)
        df_custom_emb = pd.DataFrame({"content4emb": content4embs, "content_emb": content_embs})
        df_custom_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_custom_emb.to_csv(custom_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_custom_data failed...")


def process_spider_data(save_path):
    try:
        bot_path = "/".join(save_path.split("/")[:-1])
        spider_emb_csv = os.path.join(bot_path, SPIDER_EMB)
        if os.path.exists(spider_emb_csv):
            df_spider_emb = pd.read_csv(spider_emb_csv, encoding="utf-8")
        else:
            df_spider_emb = pd.DataFrame({"content4emb": [], "content_emb": []})

        with open(save_path, "r") as file:
            text = file.read()
        docs = text_splitter.create_documents([text])
        content4embs = [doc.page_content for doc in docs]

        content_embs = get_emb_with_cache(df_spider_emb, content4embs)
        df_spider_emb = pd.DataFrame({"content4emb": content4embs, "content_emb": content_embs})
        df_spider_emb.drop_duplicates(subset='content4emb', inplace=True)
        df_spider_emb.to_csv(spider_emb_csv, index=False, encoding="utf-8")
    except:
        logger.exception("process_spider_data failed...")
