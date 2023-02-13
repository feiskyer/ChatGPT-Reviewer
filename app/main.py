#!/usr/bin/env python
# encoding: utf-8
import json
import os
from completion import *
from githubs import *


if os.getenv("GITHUB_TOKEN") == "":
    print("Please set the GITHUB_TOKEN environment variable")
    exit(1)

if os.getenv("OPENAI_API_KEY") == "":
    print("Please set the OPENAI_API_KEY environment variable")
    exit(1)


with open('/github/workflow/event.json', encoding='utf-8') as ev:
    payload = json.load(ev)

eventType = getEventType(payload)
print(f"Evaluating {eventType} event")

if eventType == EVENT_TYPE_PULL_REQUEST:
    pr, changes = getPullRequest(payload)
    prompt = getPRReviewPrompt(pr.title, pr.body, changes)
    completion_text = getCompletion(prompt)
    reviewComments = f'''@{pr.user.login} Thanks for your PR! Here are some review comments from ChatGPT:\n\n''' + completion_text
    pr.create_issue_comment(reviewComments)
else:
    print(f"{eventType} event is not supported yet, skipping")
