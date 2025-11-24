# Jules PR Comment Action

This GitHub Action posts a comment on a Pull Request with details from an associated Jules session. It detects the Jules session ID from the PR description, fetches session details and artifacts (like media), and posts a summary comment.

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `pr_number` | The Pull Request number. | **Yes** | |
| `jules_api_key` | The API key for accessing Jules services. | **Yes** | |
| `pr_description` | The Pull Request description. If not provided, it will be fetched using the API. | No | `''` |

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
        uses: BeksOmega/jules-publish@v1.0.0  # Replace with actual repository path
        with:
          pr_number: ${{ github.event.pull_request.number }}
          jules_api_key: ${{ secrets.JULES_API_KEY }}
          # pr_description: ${{ github.event.pull_request.body }} # Optional
```
