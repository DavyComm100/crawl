# -*- coding: utf-8 -*-

import json

import requests
import logging

import tiktoken
from boltons.iterutils import remap
from concurrent_log import ConcurrentTimedRotatingFileHandler
import re

BOT_SRC_DIR = "bot_resources"
EMAIL_HISTORY_EMB = "email_history_emb.csv"
CHAT_HISTORY_EMB = "chat_history_emb.csv"
BOT_EMB = "bot_emb.csv"
KB_EMB = "kb_emb.csv"
CUSTOM_EMB = "custom_emb.csv"
SPIDER_EMB = "spider_emb.csv"

# 日志配置
logger = logging.getLogger("email_bot_logger")
logger.setLevel(logging.INFO)
handler = ConcurrentTimedRotatingFileHandler(
    filename="log/email_bot", when="MIDNIGHT", interval=1, backupCount=3, encoding="utf-8"
)
handler.suffix = "%Y-%m-%d.log"
handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


def download_data(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)
    return save_path


def extract_email_history(json_obj):
    content4emb, email_history = [], []
    content4emb.append(json_obj["subject"])
    for email_content in json_obj["history"]:
        text = email_content.split("Subject:")[1].strip()
        content4emb.append(text)

        person = email_content.split("\n")[0].replace("From:", "").strip()
        email_history.append(person + ":" + text)
    return content4emb, email_history


def filter_empty_mess(messages):
    filtered_messes = []
    for m in messages:
        if m.strip() == "" or m.split(":")[1].strip() == "":
            continue
        else:
            filtered_messes.append(m)
    return filtered_messes


def count_token(prompt):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(prompt))


def truncate_massages(messages, token_limit):
    messages_final = []
    cur_tok_cnt = 0
    cur_i = 0
    for i in range(len(messages) - 1, -1, -1):
        cur_tok_cnt = cur_tok_cnt + count_token(messages[i])
        if cur_tok_cnt > token_limit:
            break
        messages_final.insert(0, messages[i])
        cur_i = i
    return messages_final, messages[:cur_i]


def extract_chat_history(json_obj):
    content4emb, chat_history = [], []
    chat_his_all_content = json_obj["content"]
    messages = chat_his_all_content.split("\n")
    for i in range(len(messages) - 1, -1, -1):
        if bool(re.match(r'^\[\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}]:', messages[i])):
            mess_splits = messages[i].split(":")
            content4emb.insert(0, ":".join(mess_splits[4:]))
            chat_history.insert(0, ":".join(mess_splits[3:]))
        else:
            messages[i - 1] = messages[i - 1] + "\\n" + messages[i]
    return "\n".join(content4emb), "\n".join(chat_history)


def extract_qa(json_obj):
    content4emb, qa = [], []
    qs = json_obj["questions"]
    qs.append(json_obj["intentName"])

    a = json_obj["answer"]
    for q in qs:
        content4emb.append(q)
        q_a = "Question:" + q + "\nAnswer:" + a
        qa.append(q_a)
    return content4emb, qa


def extract_kb(json_obj):
    content4emb, qa = [], []
    qs = json_obj["similarQuestions"]
    qs.append(json_obj["title"])

    a = json_obj["content"]
    for q in qs:
        content4emb.append(q)
        q_a = "Question:" + q + "\nAnswer:" + a
        qa.append(q_a)
    return content4emb, qa


def remove_dic_null(dic):
    doc_temp = remap(dic, visit=lambda path, key, value: value is not None and value != "" and value != [])
    return doc_temp


def parse_json(text):
    try:
        state = json.loads(text)
        state = remove_dic_null(state)
    except Exception:
        try:
            result = re.sub(r',(?=\s*})', '', text)  # 匹配逗号后面紧跟着的大括号，去掉该逗号
            state = json.loads(result)
            state = remove_dic_null(state)
        except:
            logger.error("can not parse json from: " + text)
            state = {}
    return state
