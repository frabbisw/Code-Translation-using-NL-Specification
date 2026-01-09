import sys
import os
import requests

organization = sys.argv[1]
project_key = sys.argv[2]
visibility = sys.argv[3]

if visibility not in ["public", "private"]:
  print("Visibility must be in public or private")
  visibility = "public"

SONAR_TOKEN = os.environ.get("SONAR_TOKEN")
if not SONAR_TOKEN:
    raise RuntimeError("SONAR_TOKEN environment variable not set")

url = "https://sonarcloud.io/api/projects/update_visibility"

params = {
    "organization": organization,
    "project": project_key,
    "visibility": visibility
}

response = requests.post(
    url,
    params=params,
    auth=(SONAR_TOKEN, "")
)

if response.status_code == 204:
    print("✅ Project visibility updated to public")
else:
    print("❌ Failed to update visibility")
    print("Status:", response.status_code)
    print("Response:", response.text)
