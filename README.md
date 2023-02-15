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
