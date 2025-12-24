import os
import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 환경 변수 가져오기
SPLUNK_URL = os.getenv("SPLUNK_URL", "https://localhost:8089")
PASSWORD = os.getenv("SPLUNK_PASSWORD")
JIRA_ACCOUNT = os.getenv("JIRA_ACCOUNT")
USERNAME = "admin"

def deploy_all_rules():
    rule_dir = "rules/"
    for filename in os.listdir(rule_dir):
        if filename.endswith(".yml"):
            file_path = os.path.join(rule_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    rule = yaml.safe_load(f)
                
                print(f"🚀 Deploying: {rule['title']} ({filename})")

                # [수정] 다양한 키(command, raw_text 등)를 유연하게 탐색
                selection = rule.get("detection", {}).get("selection", {})
                search_keyword = selection.get("command") or selection.get("raw_text") or "*"

                payload = {
                    "name": rule['title'],
                    "search": f'index=* source="/tmp/test.log" "{search_keyword}"',
                    "description": rule.get('description', ''),
                    "alert_type": "number of events",
                    "alert_comparator": "greater than",
                    "alert_threshold": "0",
                    "cron_schedule": "* * * * *",
                    "is_scheduled": "1",
                    "action.jira_service_desk_simple_addon": "1",
                    "action.jira_service_desk_simple_addon.param.account": JIRA_ACCOUNT,
                    "action.jira_service_desk_simple_addon.param.project": "SMS",
                    "action.jira_service_desk_simple_addon.param.issue_type": "Task"
                }

                # [팁] 중복 시 업데이트하려면 URL에 이름 추가: .../saved/searches/{rule_name}
                api_endpoint = f"{SPLUNK_URL}/servicesNS/admin/search/saved/searches"
                response = requests.post(api_endpoint, data=payload, auth=(USERNAME, PASSWORD), verify=False)

                if response.status_code in [201, 200]:
                    print(f"  ✅ Success!")
                else:
                    print(f"  ❌ Failed: {response.json()['messages'][0]['text']}")

            except Exception as e:
                print(f"  ⚠️ Error processing {filename}: {e}")

if __name__ == "__main__":
    deploy_all_rules()