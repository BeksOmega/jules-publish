import os
import re
import requests
import sys
import base64

def main():
    pr_description = os.environ.get('PR_DESCRIPTION', '')
    pr_number = os.environ.get('PR_NUMBER')
    repo_full_name = os.environ.get('REPO_FULL_NAME')
    jules_api_key = os.environ.get('JULES_API_KEY')
    github_token = os.environ.get('GITHUB_TOKEN')

    if not all([pr_number, repo_full_name, jules_api_key, github_token]):
        print("Missing required environment variables.")
        sys.exit(1)

    github_headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Fetch PR description if not provided
    if not pr_description:
        print("PR description not found in env, fetching from GitHub...")
        pr_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        try:
            response = requests.get(pr_url, headers=github_headers)
            response.raise_for_status()
            pr_data = response.json()
            pr_description = pr_data.get('body', '')
        except Exception as e:
            print(f"Error fetching PR details: {e}")
            sys.exit(1)

    # Extract session ID
    match = re.search(r'task \[(\d+)\]', pr_description)
    if not match:
        print("Not a Jules PR (no task ID found in description).")
        sys.exit(0)

    session_id = match.group(1)
    print(f"Found Jules session ID: {session_id}")

    headers = {
        'X-Goog-Api-Key': jules_api_key,
        'Content-Type': 'application/json'
    }

    # Fetch Session Details (for prompt)
    session_url = f"https://jules.googleapis.com/v1alpha/sessions/{session_id}"
    try:
        response = requests.get(session_url, headers=headers)
        response.raise_for_status()
        session_data = response.json()
        original_prompt = session_data.get('prompt', 'No prompt found')
    except Exception as e:
        print(f"Error fetching session details: {e}")
        sys.exit(1)

    # Fetch Activities (for media artifact)
    activities_url = f"https://jules.googleapis.com/v1alpha/sessions/{session_id}/activities"
    latest_media = None

    try:
        response = requests.get(activities_url, headers=headers)
        response.raise_for_status()
        activities_data = response.json()

        activities = activities_data.get('activities', [])

        # Sort by createTime to be sure we get the latest
        activities.sort(key=lambda x: x.get('createTime', ''), reverse=True)

        for activity in activities:
            artifacts = activity.get('artifacts', [])
            for artifact in artifacts:
                if 'media' in artifact:
                    latest_media = artifact['media']
                    break
            if latest_media:
                break

    except Exception as e:
        print(f"Error fetching activities: {e}")
        pass

    # Construct Comment
    comment_body = f"### Jules Task Info\n\n**Original Prompt:**\n{original_prompt}\n"

    if latest_media:
        mime_type = latest_media.get('mimeType', 'application/octet-stream')

        # Check if we have a direct URL (not in current schema but good practice)
        media_url = latest_media.get('uri')
        if media_url:
             if mime_type.startswith('image/'):
                 comment_body += f"\n**Latest Media Artifact:**\n\n![Media Artifact]({media_url})"
             else:
                 comment_body += f"\n**Latest Media Artifact:**\n\n[Download Media]({media_url})"
        elif 'data' in latest_media:
            # Handle base64 data
            try:
                data = latest_media['data']
                # Decode and save to file for artifact upload
                # Determine extension from mime type
                ext = mime_type.split('/')[-1] if '/' in mime_type else 'bin'
                filename = f"jules_artifact.{ext}"

                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data))

                print(f"Saved media artifact to {filename}")

                comment_body += f"\n**Latest Media Artifact:**\n\nA media artifact ({mime_type}) was found and has been uploaded as a workflow artifact named `{filename}`."
            except Exception as e:
                print(f"Error processing media data: {e}")
                comment_body += "\n**Latest Media Artifact:**\n\nError processing media artifact data."
        else:
            comment_body += "\n**Latest Media Artifact:**\n\nMedia artifact found but contains no data."
    else:
        comment_body += "\n**Latest Media Artifact:**\n\nNo media artifacts found."

    # Post Comment to GitHub
    github_comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"

    try:
        response = requests.post(github_comment_url, headers=github_headers, json={'body': comment_body})
        response.raise_for_status()
        print("Successfully posted comment.")
    except Exception as e:
        print(f"Error posting comment to GitHub: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
