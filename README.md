# Jules PR Comment Action

[![Built with Jules](https://img.shields.io/badge/Built%20with-Jules-715cd7?link=https://jules.google)](https://jules.google)

This GitHub Action posts a comment on a Pull Request with details from an associated [Jules](https://jules.google) session. It detects the Jules session ID from the PR description, fetches session details and artifacts (like media), and posts a summary comment.

## Prerequisites

Before using this action, you must have:

1.  **Authenticated with GitHub at [jules.google.com](https://jules.google.com).**
2.  **A Jules API Key:** Generate an API key from your Jules account settings. For more information, see the [Jules API documentation](https://developers.google.com/jules/api).
3.  **Stored the API key as a secret:** You will need to add this as a secret in your GitHub repository. For more information, see the [GitHub documentation on using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

## Inputs

| Input | Description | Required | Default |
| :--- | :--- | :--- | :--- |
| `pr_number` | The Pull Request number. | `true` | |
| `jules_api_key` | The API key for accessing Jules services. | `true` | |
| `pr_description` | The Pull Request description. If not provided, it will be fetched using the API. | `false` | `''` |

## Usage

To use this action in your workflow, add the following step. Replace `owner/repo` with the path to this repository.

```yaml
name: Jules Comment Workflow

on:
  pull_request:
    types: [opened]

jobs:
  jules_comment:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Post Jules Comment
        uses: BeksOmega/jules-publish@v1.0.0
        with:
          pr_number: ${{ github.event.pull_request.number }}
          jules_api_key: ${{ secrets.JULES_API_KEY }}
          # pr_description: ${{ github.event.pull_request.body }} # Optional
```

## Attribution

If you find this action useful, spread the word by adding the "Built with Jules" shield to your `README.md`:

```markdown
[![Built with Jules](https://img.shields.io/badge/Built%20with-Jules-715cd7?link=https://jules.google)](https://jules.google)
```

## Learn More

For more information on Jules and how to get the most out of it, please visit the [Jules documentation](https://jules.google/docs).
