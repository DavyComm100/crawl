# -*- coding: utf-8 -*-
from data_process_helper import *
from spider_helper import *
from prompt_helper import *
from emb_helper import *

from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()


class HistoryItem(BaseModel):
    content: str


class Context(BaseModel):
    subject: str
    history: List[HistoryItem]


class QueryBody(BaseModel):
    siteId: str
    query: str
    context: Context


class CreateBody(BaseModel):
    siteId: int  # 每个site代表一个客户
    emailHistoryDataUrl: Optional[str]
    chatHistoryDataUrl: Optional[str]
    botDataUrl: Optional[str]
    kbDataUrl: Optional[str]
    websiteUrl: Optional[str]
    customDataUrl: Optional[str]


@app.get("/")
def welcome():
    return "Hello, my friend. Welcome to Comm100GPT"


@app.post("/upd_cre_ate")
def upd_cre_ate(cb: CreateBody):
    # 创建workspace
    bot_name = "site_" + str(cb.siteId)
    bot_path = os.path.join(BOT_SRC_DIR, bot_name)
    if not os.path.exists(bot_path):
        os.makedirs(bot_path)

    # 1. 下载数据（全量覆盖）
    # 2. 索引构建
    try:
        if cb.emailHistoryDataUrl is not None and cb.emailHistoryDataUrl.strip() != "":
            save_path = download_data(cb.emailHistoryDataUrl.strip(), os.path.join(bot_path, "email_history_data.jsonl"))
            df_eml_his_emb = process_eml_his_data(save_path)
            logger.info("{} eml_his_emb successfully---{}".format(bot_name, df_eml_his_emb))
        if cb.chatHistoryDataUrl is not None and cb.chatHistoryDataUrl.strip() != "":
            save_path = download_data(cb.chatHistoryDataUrl.strip(), os.path.join(bot_path, "chat_history_data.jsonl"))
            df_chat_his_emb = process_chat_his_data(save_path)
            logger.info("{} chat_his_emb successfully---{}".format(bot_name, df_chat_his_emb))
        if cb.botDataUrl is not None and cb.botDataUrl.strip() != "":
            save_path = download_data(cb.botDataUrl.strip(), os.path.join(bot_path, "bot_data.jsonl"))
            df_bot_emb = process_bot_data(save_path)
            logger.info("{} bot_emb successfully---{}".format(bot_name, df_bot_emb))
        if cb.kbDataUrl is not None and cb.kbDataUrl.strip() != "":
            save_path = download_data(cb.kbDataUrl.strip(), os.path.join(bot_path, "kb_data.jsonl"))
            df_kb_emb = process_kb_data(save_path)
            logger.info("{} kb_emb successfully---{}".format(bot_name, df_kb_emb))
        if cb.customDataUrl is not None and cb.customDataUrl.strip() != "":  # 1.0版本先只支持文本文件
            save_path = download_data(cb.customDataUrl.strip(), os.path.join(bot_path, "custom_data.txt"))
            df_custom_emb = process_custom_data(save_path)
            logger.info("{} custom_emb successfully---{}".format(bot_name, df_custom_emb))
        if cb.websiteUrl is not None and cb.websiteUrl.strip() != "":
            save_path = crawl(cb.websiteUrl.strip(), os.path.join(bot_path, "spider_data.txt"))
            df_spider_emb = process_spider_data(save_path)
            logger.info("{} spider_url_emb successfully---{}".format(bot_name, df_spider_emb))
        return {'code': 0, 'msg': 'success'}
    except:
        logger.exception("call answer failed......")
        return {'code': -1, 'msg': 'failed'}


@app.post("/query")
def query(qb: QueryBody):
    print("{} is processing...".format(os.getpid()))
    start_time = time.time()

    bot_name = "site_" + str(qb.siteId)
    bot_path = os.path.join(BOT_SRC_DIR, bot_name)
    if not os.path.exists(bot_path):
        return {'code': -2, 'msg': "site {} agent doesn't exist...".format(qb.siteId)}

    try:
        # 记忆填充
        qb.context.history.append(qb.query)
        content4emb, email_history = extract_email_history(qb.context)
        email_history = filter_empty_mess(email_history)
        email_history, truncated = truncate_massages(email_history, 1500)

        # runtime memory summary
        if len(truncated) > 1:
            remain_ms, _ = truncate_massages(truncated, 3500)
            chat_his_summary_prompt = gen_chat_his_summary_prompt("".join(remain_ms))
            chat_his_summary = get_chat_res(chat_his_summary_prompt)
            chat_his_ctx = build_chat_his_ctx(chat_his_summary)
            email_history.insert(0, chat_his_ctx)

        content4emb = "\n".join(content4emb)
        email_history = "\n".join(email_history)

        # user_query embedding生成
        embs = get_emb([content4emb])

        # Context生成
        all_context = []

        # 1. EMAIL_HISTORY_EMB
        eml_his_emb_path = os.path.join(bot_path, EMAIL_HISTORY_EMB)
        if os.path.exists(eml_his_emb_path):
            eml_context = gen_emb_context(embs, eml_his_emb_path, eml_emb_sim_threshold, eml_emb_sim_cand_num)
            all_context.extend(eml_context)
        # 2. CHAT_HISTORY_EMB
        chat_his_emb_path = os.path.join(bot_path, CHAT_HISTORY_EMB)
        if os.path.exists(chat_his_emb_path):
            chat_context = gen_emb_context(embs, chat_his_emb_path, chat_emb_sim_threshold, chat_emb_sim_cand_num)
            all_context.extend(chat_context)
        # 3. BOT_EMB
        bot_emb_path = os.path.join(bot_path, BOT_EMB)
        if os.path.exists(bot_emb_path):
            bot_context = gen_emb_context(embs, bot_emb_path, bot_emb_sim_threshold, bot_emb_sim_cand_num)
            all_context.extend(bot_context)
        # 4. KB_EMB
        kb_emb_path = os.path.join(bot_path, KB_EMB)
        if os.path.exists(kb_emb_path):
            kb_context = gen_emb_context(embs, kb_emb_path, kb_emb_sim_threshold, kb_emb_sim_cand_num)
            all_context.extend(kb_context)
        # 5. CUSTOM_EMB
        custom_emb_path = os.path.join(bot_path, CUSTOM_EMB)
        if os.path.exists(custom_emb_path):
            custom_context = gen_emb_context(embs, custom_emb_path, custom_emb_sim_threshold, custom_emb_sim_cand_num)
            all_context.extend(custom_context)
        # 6. SPIDER_EMB
        spider_emb_path = os.path.join(bot_path, SPIDER_EMB)
        if os.path.exists(spider_emb_path):
            spider_context = gen_emb_context(embs, spider_emb_path, spider_emb_sim_threshold, spider_emb_sim_cand_num)
            all_context.extend(spider_context)

        all_context.reverse()
        remain_ctx, _ = truncate_massages(all_context, 2500)
        remain_ctx = "\n".join(remain_ctx)

        # 答案生成
        prompt = gen_retrieve_prompt(remain_ctx, email_history)
        chat_res = get_chat_res(prompt)
        chat_res = parse_json(chat_res)

        return {'code': 0, 'msg': 'success', 'data': chat_res["reply"], 'cost': time.time() - start_time}
    except Exception:
        logger.exception("call query failed......")
        return {'code': -1, 'msg': 'failed'}

# @app.post("/refresh")
# def refresh(rb: RefreshBody):
#     """
#     更新intents.txt、priority.txt后，需要手动刷新才生效
#     {
#         "bot_name": "xxxxxx",  # 要操作的bot name
#         "operate": "upsert",  # 操作。upsert：更新或新增；delete：删除
#     }
#     """
#     start = datetime.datetime.now()
#
#     resq_data = json.loads(request.get_data())
#     bot_n = resq_data["bot_name"].strip()
#     operate = resq_data["operate"].strip()
#
#     # 加锁
#     bot_lock = redis_lock.Lock(r, "lock_" + bot_n)
#     if bot_lock.acquire(blocking=False):
#         if operate == "upsert":
#             build_bot_intents_dict_trie(bot_n)
#             print(bot_n, "intents dict and trie finished rebuilding...")
#
#             index_dir_ = os.path.join(BOT_SRC_DIR, bot_n, "index")
#             if not os.path.exists(index_dir_):
#                 os.mkdir(index_dir_)
#             build_bot_whoosh_index(bot_n, index_dir_)
#             print(bot_n, "whoosh index finished rebuilding...")
#
#             build_bot_priorities(bot_n)
#             print(bot_n, "priority file finished reloading...")
#
#             r_v = r.hincrby("bot_version", bot_n)
#             r.hset("bot_version&" + bot_n, str(os.getpid()), r_v)
#
#             ret = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
#         elif operate == "delete":
#             # 删除bot
#             bot_path = os.path.join(BOT_SRC_DIR, bot_n)
#             if os.path.exists(bot_path):
#                 shutil.rmtree(bot_path)
#             r.delete("bot_intents&" + bot_n)
#             r.delete("bot_intents_whoosh&" + bot_n)
#             r.delete("bot_recent&" + bot_n)
#             r.delete("bot_frequency&" + bot_n)
#             r.delete("bot_priorities&" + bot_n)
#             r.delete("bot_version&" + bot_n)
#             r.hdel("bot_trie", bot_n)
#             r.hdel("bot_whoosh", bot_n)
#             r.hdel("bot_version", bot_n)
#
#             del_dict_key(bot_intents_dict, bot_n)
#             del_dict_key(bot_intents_whoosh_dict, bot_n)
#             del_dict_key(bot_recents, bot_n)
#             del_dict_key(bot_frequency, bot_n)
#             del_dict_key(bot_priorities, bot_n)
#             del_dict_key(bot_trie, bot_n)
#             del_dict_key(bot_searcher, bot_n)
#             del_dict_key(bot_qp, bot_n)
#
#             ret = {'code': 0, 'msg': 'success', 'time_cost': time_cost(start)}
#         else:
#             ret = {'code': -1, 'msg': 'unsupported operation', 'time_cost': time_cost(start)}
#
#         bot_lock.release()
#         return ret
#     else:
#         return {'code': -2, 'msg': 'someone is refreshing this bot, please wait.', 'time_cost': time_cost(start)}
