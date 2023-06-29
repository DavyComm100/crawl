# -*- coding: utf-8 -*-

def gen_chat_his_summary_prompt(chat_his):
    prompt_str = """GOAL:
You are a trustworthy human mail reply agent, your task is to create a concise running summary based on the DIALOGUE below, focusing on key and potentially important information to remember.

CONSTRAINT:
1. Keeping the summary concise, within 400 words.
2. Remember to strictly adhere to all the provisions of this CONSTRAINT.

DIALOGUE:
{}""".format(chat_his)
    return prompt_str


def build_chat_his_ctx(chat_his_summary):
    if "I don't know".lower() not in chat_his_summary.lower():
        return "Context:" + chat_his_summary + "\n"


def gen_retrieve_prompt(qa_retrieve_ctx, transed_dialogue):
    prompt_str = """GOAL:
You are a trustworthy human mail reply agent, with reference to the SIMILAR EVENTS below, generate the most appropriate reply based on the DIALOGUE below.

SIMILAR EVENTS:
{}

CONSTRAINT:
1. Make sure you are not trying to make up the answer, especially when it comes to things beyond the boundaries of your ability and cognition.
2. You should only respond in JSON format as described below, and ensure the response can be parsed by Python json.loads:
{{
    "reasoning": "reasoning",
    "plan": "list that conveys and give long-term plans",
    "criticism": "constructive self-criticism",
    "reply": "summary to reply based on the DIALOGUE below"
}}
3. Remember to strictly adhere to all the provisions of this CONSTRAINT.

DIALOGUE:
{}""".format(qa_retrieve_ctx, transed_dialogue)
    # logger.info(prompt_str)
    return prompt_str
