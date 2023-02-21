#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import requests
from github import Github


# List of event types
EVENT_TYPE_PUSH = "push"
EVENT_TYPE_COMMENT = "comment"
EVENT_TYPE_PULL_REQUEST = "pull_request"
EVENT_TYPE_OTHER = "other"


class GithubClient:
    '''Github API client'''

    def __init__(self, openai_client, review_per_file=False, comment_per_file=False, blocking=False):
        self.openai_client = openai_client
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_client = Github(self.github_token)
        self.review_tokens = self.openai_client.max_tokens - self.openai_client.min_tokens
        self.review_per_file = review_per_file
        self.comment_per_file = comment_per_file
        self.blocking = blocking

    def get_event_type(self, payload) -> str:
        '''Determine the type of event'''
        if payload.get("head_commit") is not None:
            return EVENT_TYPE_PUSH

        if payload.get("pull_request") is not None:
            return EVENT_TYPE_PULL_REQUEST

        if payload.get("comment") is not None:
            return EVENT_TYPE_COMMENT

        return EVENT_TYPE_OTHER

    def get_pull_request(self, payload):
        '''Get the pull request'''
        repo = self.github_client.get_repo(os.getenv("GITHUB_REPOSITORY"))
        pr = repo.get_pull(payload.get("number"))
        changes = requests.get(pr.url,
                               timeout=30,
                               headers={"Authorization": "Bearer " + self.github_token,
                                        "Accept": "application/vnd.github.v3.diff"},
                               ).text
        return pr, changes

    def cut_changes(self, previous_filename, filename, patch):
        '''Cut the changes to fit the max tokens'''
        if previous_filename is None:
            previous_filename = filename

        # add a patch header
        patch = f'diff --git a/{previous_filename} b/{filename}\n{patch}'
        if len(self.openai_client.encoder.encode(patch)) < self.review_tokens:
            return patch

        # TODO: it is not a good idea to cut the contents, need figure out a better way
        lines = patch.splitlines()
        print(
            f"The changes for {filename} is too long, contents would be cut to fit the max tokens")
        i = len(lines)
        while i > 0:
            i -= 1
            line = '\n'.join(lines[:i])
            if len(self.openai_client.encoder.encode(line)) < self.review_tokens:
                return line
        return ''

    def get_completion(self, prompt) -> str:
        '''Get the completion'''
        try:
            completion = self.openai_client.get_completion(prompt)
            return completion
        except Exception as e:
            if self.blocking:
                raise e
            else:
                print(f"OpenAI failed on prompt {prompt} with exception {e}")
                return ''

    def review_pr(self, payload):
        '''Review a PR'''
        pr, changes = self.get_pull_request(payload)
        if len(self.openai_client.encoder.encode(changes)) < self.review_tokens and not self.review_per_file:
            # Review the full PR changes together
            prompt = self.openai_client.get_pr_prompt(
                pr.title, pr.body, changes)
            completion = self.get_completion(prompt)
            if completion != '':
                reviewComments = f'''@{pr.user.login} Thanks for your contributions!\n\n{completion}'''
                pr.create_issue_comment(reviewComments)
            return

        # Review each file changes separately
        files_changed = pr.get_files()
        reviews = []
        for file in files_changed:
            file_changes = self.cut_changes(
                file.previous_filename, file.filename, file.patch)
            prompt = self.openai_client.get_file_prompt(
                pr.title, pr.body, file.filename, file_changes)
            completion = self.get_completion(prompt)
            if completion == '':
                continue
            if self.comment_per_file:
                # Create a review comment on the file
                reviewComments = f'''@{pr.user.login} Thanks for your contributions!\n\n{completion}'''
                pr.create_review_comment(body=reviewComments,
                                         commit_id=list(pr.get_commits())[-1],
                                         path=file.filename,
                                         position=1)
            else:
                reviews = reviews + \
                    [f"**Here are review comments for file {file.filename}:**\n{completion}\n\n"]

        if len(reviews) > 0:
            # Create a review comment on the PR
            reviewComments = f'''@{pr.user.login} Thanks for your contributions!\n\n{''.join(reviews)}'''
            pr.create_issue_comment(reviewComments)
