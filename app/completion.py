#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import backoff
import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
if os.getenv("OPENAI_API_BASE"):
    openai.api_base = os.getenv("OPENAI_API_BASE")
    if "azure" in os.getenv("OPENAI_API_BASE"):
        openai.api_type = "azure"
        openai.api_version = "2023-03-15-preview"
system_prompt = '''As a tech reviewer, please provide an in-depth review of the
following pull request git diff data. Your task is to carefully analyze the title, body, and
changes made in the pull request and identify any problems that need addressing including 
security issues. Please provide clear descriptions of each problem and offer constructive 
suggestions for how to address them. Additionally, please consider ways to optimize the 
changes made in the pull request. You should focus on providing feedback that will help
improve the quality of the codebase while also remaining concise and clear in your
explanations. Please note that unnecessary explanations or summaries should be avoided
as they may delay the review process. Your feedback should be provided in a timely
manner, using language that is easy to understand and follow.
'''


class OpenAIClient:
    '''OpenAI API client'''

    def __init__(self, model, temperature, frequency_penalty, presence_penalty,
                 max_tokens=4000, min_tokens=256):
        self.model = model
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.encoder = tiktoken.get_encoding("gpt2")
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.openai_kwargs = {'model': self.model}
        if openai.api_type == "azure":
            self.openai_kwargs = {'engine': self.model}

    @backoff.on_exception(backoff.expo,
                          (openai.error.RateLimitError,
                           openai.error.APIConnectionError,
                           openai.error.ServiceUnavailableError),
                          max_time=300)
    def get_completion(self, prompt) -> str:
        if self.model.startswith("gpt-"):
            return self.get_completion_chat(prompt)
        else:
            return self.get_completion_text(prompt)

    def get_completion_chat(self, prompt) -> str:
        '''Invoke OpenAI API to get chat completion'''
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = openai.ChatCompletion.create(
            messages=messages,
            temperature=self.temperature,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            request_timeout=100,
            max_tokens=self.max_tokens - len(self.encoder.encode(f'{system_prompt}\n{prompt}')),
            stream=True, **self.openai_kwargs)

        completion_text = ''
        for event in response:
            if event["choices"] is not None and len(event["choices"]) > 0:
                choice = event["choices"][0]
                if choice.get("delta", None) is not None and choice["delta"].get("content", None) is not None:
                    completion_text += choice["delta"]["content"]
                if choice.get("message", None) is not None and choice["message"].get("content", None) is not None:
                    completion_text += choice["message"]["content"]
        return completion_text

    def get_completion_text(self, prompt) -> str:
        '''Invoke OpenAI API to get text completion'''
        prompt_message = f'{system_prompt}\n{prompt}'
        response = openai.Completion.create(
            prompt=prompt_message,
            temperature=self.temperature,
            best_of=1,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            request_timeout=100,
            max_tokens=self.max_tokens - len(self.encoder.encode(prompt_message)),
            stream=True, **self.openai_kwargs)

        completion_text = ''
        for event in response:
            if event["choices"] is not None and len(event["choices"]) > 0:
                completion_text += event["choices"][0]["text"]
        return completion_text

    def get_pr_prompt(self, title, body, changes) -> str:
        '''Generate a prompt for a PR review'''
        prompt = f'''Here are the title, body and changes for this pull request:

Title: {title}

Body: {body}

Changes:
```
{changes}
```
    '''
        return prompt

    def get_file_prompt(self, title, body, filename, changes) -> str:
        '''Generate a prompt for a file review'''
        prompt = f'''Here are the title, body and changes for this pull request:

Title: {title}

Body: {body}

And bellowing are changes for file {filename}:
```
{changes}
```
    '''
        return prompt
