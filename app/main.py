#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import os
import argparse
import distutils
import completion
import githubs


# Check required environment variables
if os.getenv("GITHUB_TOKEN") == "":
    print("Please set the GITHUB_TOKEN environment variable")
    exit(1)
if os.getenv("OPENAI_API_KEY") == "":
    print("Please set the OPENAI_API_KEY environment variable")
    exit(1)

# Parse arguments
parser = argparse.ArgumentParser(
    description='Automated pull requests reviewing and issues triaging with ChatGPT')
parser.add_argument("--model",
                    help="OpenAI model",
                    type=str, default="gpt-3.5-turbo")
parser.add_argument("--temperature",
                    help="Temperature for the model",
                    type=float, default=0.2)
parser.add_argument("--frequency-penalty",
                    help="Frequency penalty for the model",
                    type=int, default=0)
parser.add_argument("--presence-penalty",
                    help="Presence penalty for the model",
                    type=int, default=0)
parser.add_argument("--review-per-file",
                    help="Send out review requests per file",
                    type=distutils.util.strtobool, default=False)
parser.add_argument("--comment-per-file",
                    help="Post review comments per file",
                    type=distutils.util.strtobool, default=True)
parser.add_argument("--blocking",
                    help="Blocking the pull requests on OpenAI failures",
                    type=distutils.util.strtobool, default=False)
args = parser.parse_args()


# Initialize clients
openai_client = completion.OpenAIClient(
    model=args.model,
    temperature=args.temperature,
    frequency_penalty=args.frequency_penalty,
    presence_penalty=args.presence_penalty)
github_client = githubs.GithubClient(
    openai_client=openai_client,
    review_per_file=args.review_per_file,
    comment_per_file=args.comment_per_file,
    blocking=args.blocking)


# Load github workflow event
with open('/github/workflow/event.json', encoding='utf-8') as ev:
    payload = json.load(ev)
eventType = github_client.get_event_type(payload)
print(f"Evaluating {eventType} event")


# Review the changes via ChatGPT
match eventType:
    case githubs.EVENT_TYPE_PULL_REQUEST:
        github_client.review_pr(payload)
    case _:
        print(f"{eventType} event is not supported yet, skipping")
