# ChatGPT-Reviewer

Automated pull requests reviewing and issues triaging with ChatGPT.

## How to use

Create an OpenAI API key [here](https://platform.openai.com/account/api-keys), and then set the key as an [action secret in your repository](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository) named `OPENAI_API_KEY`.

Finally, create a file named `.github/workflows/chatgpt-review.yml` with the following contents:

```yaml
name: ChatGPT Review

on: [pull_request]


jobs:
  chatgpt-review:
    name: ChatGPT Review
    runs-on: ubuntu-latest
    steps:
    - uses: feiskyer/ChatGPT-Reviewer@v0.3
      name: ChatGPT Review
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Samples

The ChatGPT reviewer PRs are also getting reviewed by ChatGPT, refer the [pull requests](https://github.com/feiskyer/ChatGPT-Reviewer/pulls?q=is%3Apr) for the sample review comments.

## Special notes for public repository forks

In order to protect public repositories for malicious users, Github runs all pull request workflows raised from repository forks with a read-only token and no access to secrets.

`pull_request_target` event could be used in such cases, which would run the workflow in the context of the base of the pull request (rather than in the context of the merge commit, as the `pull_request` event does).

Refer Github docs [here](https://docs.github.com/en/github-ae@latest/actions/using-workflows/events-that-trigger-workflows#pull_request_target) for more details of `pull_request_target` event.
