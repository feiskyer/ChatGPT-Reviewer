# encoding: utf-8
import os
import backoff
import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
ENCODER = tiktoken.get_encoding("gpt2")
MODEL = "text-davinci-003"


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
        max_tokens=4000 - len(ENCODER.encode(prompt)),
        stop="\n\n\n",
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

Changes: {changes}
'''
    return prompt
