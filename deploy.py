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
    
    # 1. 폴더 내 모든 .yml 파일 탐색
    for filename in os.listdir(rule_dir):
        if filename.endswith(".yml"):
            file_path = os.path.join(rule_dir, filename)
            
            with open(file_path, 'r') as f:
                rule = yaml.safe_load(f)
            
            print(f"🚀 Deploying: {rule['title']} ({filename})")

            # 2. Payload 구성 (YAML 내용 기반)
            payload = {
                "name": rule['title'],
                "search": f'index=* source="/tmp/test.log" "{rule["detection"]["selection"]["command"]}"',
                "description": rule['description'],
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

            # 3. Splunk API 전송
            api_endpoint = f"{SPLUNK_URL}/servicesNS/admin/search/saved/searches"
            response = requests.post(api_endpoint, data=payload, auth=(USERNAME, PASSWORD), verify=False)

            if response.status_code in [201, 200]:
                print(f"✅ Success!")
            else:
                print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    deploy_all_rules()