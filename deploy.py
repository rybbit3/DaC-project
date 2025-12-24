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

                # [개선] command가 없으면 raw_text를 찾고, 둘 다 없으면 기본 키워드 적용
                selection = rule.get("detection", {}).get("selection", {})
                search_keyword = selection.get("command") or selection.get("raw_text") or "SECURITY_ALERT"

                payload = {
                    "name": rule['title'],
                    "search": f'index=* source="/tmp/test.log" "{search_keyword}"',
                    "description": rule.get('description', 'Deployed via DaC'),
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

                api_endpoint = f"{SPLUNK_URL}/servicesNS/admin/search/saved/searches"
                response = requests.post(api_endpoint, data=payload, auth=(USERNAME, PASSWORD), verify=False)

                if response.status_code in [201, 200]:
                    print(f"  ✅ Success!")
                else:
                    print(f"  ❌ Failed: {response.text}")

            except Exception as e:
                # 에러가 발생해도 스크립트가 멈추지 않고 다음 파일로 넘어가도록 처리
                print(f"  ⚠️ Error processing {filename}: {e}")

if __name__ == "__main__":
    deploy_all_rules()