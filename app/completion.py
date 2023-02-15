#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import backoff
import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = "text-davinci-003"
# ENCODER = tiktoken.get_encoding("gpt2")
ENCODER = tiktoken.encoding_for_model(MODEL)
MAX_TOKENS = 4097
MIN_TOKENS = 256


@backoff.on_exception(backoff.expo,
                      (openai.error.RateLimitError,
                       openai.error.APIConnectionError,
                       openai.error.ServiceUnavailableError),
                      max_time=300)
def getCompletion(prompt) -> str:
    '''Invoke OpenAI API to get completion text'''
    response = openai.Completion.create(
        model=MODEL,
        prompt=prompt,
        temperature=0,
        best_of=1,
        frequency_penalty=0,
        presence_penalty=0,
        request_timeout=100,
        max_tokens=MAX_TOKENS - len(ENCODER.encode(prompt)),
        stream=True)

    completion_text = ''
    for event in response:
        if event["choices"] is not None and len(event["choices"]) > 0:
            completion_text += event["choices"][0]["text"]
    return completion_text


def getPRReviewPrompt(title, body, changes) -> str:
    '''Generate a prompt for a PR review'''
    prompt = f'''I want you to act as a tech reviewer for pull requests and you will provide me with an in-depth review, including the problems and suggestions.

Here are the title, body and changes for this pull request:

Title: {title}

Body: {body}

Changes:
```
{changes}
```
'''
    return prompt


def cutChanges(chunk):
    '''Cut the changes to fit the max tokens'''
    # TODO: it is not a good idea to cut the contents, need figure out a better way
    chunk = 'diff --git' + chunk
    if len(ENCODER.encode(chunk)) < MAX_TOKENS - MIN_TOKENS:
        return chunk

    lines = chunk.splitlines()
    filename = lines[0]
    print(
        f"The changes for {filename} is too long, contents would be cut to fit the max tokens")
    i = len(lines)
    while i > 0:
        i -= 1
        line = '\n'.join(lines[:i])
        if len(ENCODER.encode(line)) < MAX_TOKENS - MIN_TOKENS:
            return line
    return ''


def getFileName(chunk):
    '''Get the file name from the chunk'''
    return chunk.splitlines()[0]


def getSplittedCompletionForDiff(title, body, changes) -> str:
    '''Split the changes by changed files to fit the max tokens'''
    chunks = [cutChanges(chunk)
              for chunk in changes.split('diff --git') if chunk != '']
    prompts = [getPRReviewPrompt(title, body, chunk) for chunk in chunks]
    completions = [getCompletion(prompt) for prompt in prompts]
    filenames = [getFileName(chunk) for chunk in chunks]
    return [f"Here are review comments for {filenames[i]}:\n{completions[i]}" for i in range(len(chunks))]


def getCompletionForDiff(title, body, changes):
    '''Get completion for a PR diff'''
    if len(ENCODER.encode(changes)) < MAX_TOKENS - MIN_TOKENS:
        prompt = getPRReviewPrompt(title, body, changes)
        completion = getCompletion(prompt)
        return [completion]

    return getSplittedCompletionForDiff(title, body, changes)
