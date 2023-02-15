#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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
    comments = getCompletionForDiff(pr.title, pr.body, changes)
    reviewComments = f'''@{pr.user.login} Thanks for your PR!\n\n'''
    for prompt in comments:
        reviewComments += prompt + "\n\n"
    pr.create_issue_comment(reviewComments)
else:
    print(f"{eventType} event is not supported yet, skipping")
