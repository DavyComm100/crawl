# -*- coding: utf-8 -*-

import time

from utils import *
import openai
from openai.error import RateLimitError, APIError

ak = "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"


def get_emb(query_arr):
    # 最大输入长度8191
    num_retries = 5
    response = None

    for _ in range(num_retries):
        try:
            openai.api_key = ak
            response = openai.Embedding.create(
                input=query_arr, engine="text-embedding-ada-002"
            )
            embs = [d["embedding"] for d in response["data"]]
            return embs
        except Exception:
            sleep_time = 0.5
            logger.exception("{} call openai embedding api failed, sleep {} second...".format(ak, sleep_time))
            time.sleep(sleep_time)
    if response is None:
        raise RuntimeError("Failed to get openai embedding response...")


def call_azure(prompt, api_url, key):
    query_body = {"temperature": 0, "messages": [{"role": "user", "content": prompt}]}
    headers = {'content-type': 'application/json', 'api-key': key}
    response = requests.post(api_url, json=query_body, headers=headers, timeout=3600)
    json_res = json.loads(response.text)
    try:
        return json_res["choices"][0]["message"]["content"]
    except:
        logger.error("call_azure failed, prompt: {}, returned json result: {}".format(prompt, json_res))
        raise RuntimeError("Failed to call_azure...")


def get_chat_res(prompt):
    try:
        return call_azure(prompt, "https://comm100gpt.openai.azure.com/openai/deployments/Summary/chat/completions?api-version=2023-03-15-preview", "3a4cc360c1f8427c9a22225197744697")
    except:
        logger.error("call_azure failed......")

    num_retries = 5
    response = None

    for _ in range(num_retries):
        try:
            openai.api_key = ak
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message["content"]
        except (RateLimitError, APIError):
            sleep_time = 0.5
            logger.error("{} call openai chat api failed, sleep {} second...".format(ak, sleep_time))
            time.sleep(sleep_time)
        except:
            logger.exception("{} call openai chat api failed with prompt: {}".format(ak, prompt))
            raise RuntimeError("Failed to get_chat_res...")
    if response is None:
        raise RuntimeError("Failed to get_chat_res...")
