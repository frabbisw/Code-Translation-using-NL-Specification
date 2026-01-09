import json
import os
import time

import requests
from requests.auth import HTTPBasicAuth

from collections import Counter
import sys

# directory = sys.argv[1]
# dataset = sys.argv[2]
# src_lang = sys.argv[3]
# target_lang = sys.argv[4]
# output_dir = sys.argv[5]
# organization = sys.argv[6]

src_dir = sys.argv[1]
tgt_path = sys.argv[2]
organization = sys.argv[3]
project_key = sys.argv[4]

# os.makedirs(output_dir, exist_ok=True)

print(f"Downloading info from sonarcloud... ", f"src_dir: {src_dir}", f"tgt_path: {tgt_path}", f"organization: {organization}", f"project_key: {project_key}")

# exit()
# Get the SonarCloud token from the environment variable
sonar_token = os.getenv('SONAR_TOKEN')

# Check if the token is retrieved
if not sonar_token:
    raise ValueError("The SONAR_TOKEN environment variable is not set.")

# API endpoint to search for issues
url = 'https://sonarcloud.io/api/issues/search'

# Initialize pagination parameters
page = 1
page_size = 100  # Number of issues per page

total_issues = []  # List to store all issues

while True:
    # Set parameters for the request
    params = {
        'componentKeys': project_key,
        'severities': 'INFO,MINOR,MAJOR,CRITICAL,BLOCKER',  # Filter by highest severities
        'resolved': 'false',  # Get only unresolved issues
        'p': page,  # Current page number
        'ps': page_size  # Page size
    }

    # Make the request
    response = requests.get(url, auth=(sonar_token, ''), params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        issues = data.get('issues', [])
        total_issues.extend(issues)  # Add issues to the total list

        # Break the loop if there are no more issues
        if len(issues) < page_size:
            break

        # Move to the next page
        page += 1
        time.sleep(1)
    else:
        print(f'Error: {response.status_code} - {response.text}')
        break

summary = {"severity": {}, "impact": {}, "sever_files": set(), "total": len(total_issues)}

# Output all collected issues
if len(total_issues) > 1:
    for issue in total_issues:
        if issue['severity'] in ["CRITICAL", "BLOCKER"]:
            summary["sever_files"].add(issue['component'])
        if issue['severity'] not in summary["severity"].keys():
            summary["severity"][issue['severity']] = 0
        summary["severity"][issue['severity']] += 1
        if "SECURITY" in [im['softwareQuality'] for im in issue['impacts']]:
            if "SECURITY" not in summary["impact"].keys():
                summary["impact"]["SECURITY"] = 0
            summary["impact"]["SECURITY"] += 1
else:
    print("No unresolved high severity issues found.")
summary["sever_files"] = len(summary["sever_files"])

time.sleep(1)

nloc_response = requests.get(url=f'https://sonarcloud.io/api/measures/component?'
                                 f'component={project_key}&metricKeys=ncloc',
                             auth=HTTPBasicAuth(sonar_token, ''))
if nloc_response.status_code == 200:
    data = nloc_response.json()
    ncloc_value = data['component']['measures'][0]['value']
    summary["ncloc"] = ncloc_value
else:
    summary["ncloc"] = "N/A"

print(f"SUMMARY: {summary}")
with open(f"{tgt_path}_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
with open(f"{tgt_path}_details.json", "w") as f:
    json.dump(total_issues, f, indent=2)

print("-" * 50)
