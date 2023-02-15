#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import requests
from github import Github


EVENT_TYPE_PUSH = "push"
EVENT_TYPE_COMMENT = "comment"
EVENT_TYPE_PULL_REQUEST = "pull_request"
EVENT_TYPE_OTHER = "other"


githubToken = os.getenv("GITHUB_TOKEN")
g = Github(githubToken)


def getEventType(payload) -> str:
    '''Determine the type of event'''
    if payload.get("head_commit") is not None:
        return EVENT_TYPE_PUSH

    if payload.get("pull_request") is not None:
        return EVENT_TYPE_PULL_REQUEST

    if payload.get("comment") is not None:
        return EVENT_TYPE_COMMENT

    return EVENT_TYPE_OTHER


def getPullRequest(payload):
    '''Get the pull request'''
    repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))
    pr = repo.get_pull(payload.get("number"))
    changes = requests.get(pr.url,
                           timeout=30,
                           headers={"Authorization": "Bearer " + githubToken,
                                    "Accept": "application/vnd.github.v3.diff"},
                           ).text
    return pr, changes
