""" This is a LLM client wrapper that we will use to interact with the LLM API. 
It exposes llm_Complete function that can be used to send a message to the LLM API and get the response.
"""

import os
import time
from typing import Optional, List, Dict, Any
import json
import logging

from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from dotenv import load_dotenv

# === Configurations & Initialization ===
load_dotenv(override=True)
client = OpenAI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Helper Functions ===
def _normalization_tool_calls(tool_calls: Optional[List[ChatCompletionMessageToolCall]]) -> List[Dict[str, Any]]:
    """ Normalize tool calls to a consistent format """
    if not tool_calls:
        return []
    normalized = []
    for tool_call in tool_calls:
        # tc.function.arguments is a JSON strign as per the SDK
        try:
            args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        except Exception as e:
            args = {}
        
        normalized.append(
            {
                "name": tool_call.function.name if tool_call.function else tool_call.type,
                "arguments": args,
            }
        )
    
    return normalized

# === LLM Client Functions ===
def llm_complete(
    system_prompt: str,
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 400,
    timeout: int = 30,
    retry: int = 1,
) -> Dict[str, Any]:
    """
    messages: list of dicts like {"role": "user"|"assistant"|"system", "content": "..."}
    tools: OpenAI tool specs (list of dicts) or None
    """

    attempt = 0
    last_err = None

    # Add system prompt to the messages
    all_messages = [{"role": "system", "content": system_prompt}] + messages

    while attempt <= retry:
        try:
            resp: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=all_messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )

            choice = resp.choices[0].message
            content = choice.content or ""
            tool_calls = _normalization_tool_calls(choice.tool_calls)
            return {"content": content, "tool_calls": tool_calls}
        except Exception as e:
            last_err = e
            logger.warning(f"LLM call failed (attempt {attempt + 1}/{retry + 1}): {e}")
            attempt += 1
            time.sleep(1)
    raise RuntimeError(f"LLM call failed after {retry + 1} attempts: {last_err}")
