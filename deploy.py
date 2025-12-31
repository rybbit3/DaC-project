import os
import yaml
import requests
import hashlib
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STATE_FILE = "deploy_state.json"
RULE_DIR = "rules/"

def get_file_hash(file_path):
    """파일의 해시값을 계산하여 내용 변경 여부 확인"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def deploy_all_rules():
    state = load_state()
    new_state = state.copy()
    
    # 환경 변수 및 기본 설정
    splunk_url = os.getenv("SPLUNK_URL", "https://localhost:8089")
    password = os.getenv("SPLUNK_PASSWORD")
    jira_acc = os.getenv("JIRA_ACCOUNT", "rybbit3")
    auth = ("admin", password)

    for filename in os.listdir(RULE_DIR):
        if filename.endswith(".yml"):
            file_path = os.path.join(RULE_DIR, filename)
            current_hash = get_file_hash(file_path)
            
            # 1. 변경 여부 확인
            if state.get(filename) == current_hash:
                print(f"⏩ Skipping: {filename} (No changes detected)")
                continue

            # 2. YAML 파싱 및 배포 준비
            with open(file_path, 'r') as f:
                rule = yaml.safe_load(f)
            
            print(f"🚀 Deploying: {rule['title']} ({filename})...")
            
            selection = rule.get("detection", {}).get("selection", {})
            keyword = selection.get("command") or selection.get("raw_text") or "*"
            
            payload = {
                "name": rule['title'],
                "search": f'index=* source="/tmp/test.log" "{keyword}"',
                "description": rule.get('description', 'Updated via State Tracking'),
                "alert_type": "number of events",
                "alert_comparator": "greater than",
                "alert_threshold": "0",
                "cron_schedule": "* * * * *",
                "is_scheduled": "1",
                "action.jira_service_desk_simple_addon": "1",
                "action.jira_service_desk_simple_addon.param.account": jira_acc,
                "action.jira_service_desk_simple_addon.param.project": "SMS",
                "action.jira_service_desk_simple_addon.param.issue_type": "Task"
            }

            # 3. 배포 (기존 룰이 있으면 업데이트하기 위해 엔드포인트에 이름 포함)
            # POST /servicesNS/admin/search/saved/searches/{rule_name} 로 보내면 업데이트됨
            api_endpoint = f"{splunk_url}/servicesNS/admin/search/saved/searches"
            
            response = requests.post(api_endpoint, data=payload, auth=auth, verify=False)

            if response.status_code in [200, 201]:
                print(f"  ✅ Success!")
                new_state[filename] = current_hash # 상태 업데이트
            elif "already exists" in response.text:
                # 이미 존재할 경우 업데이트 로직으로 재시도 가능 (선택 사항)
                print(f"  ⚠️ Exists, but hash is different. Please update manually or adjust API endpoint.")
            else:
                print(f"  ❌ Failed: {response.text}")

    save_state(new_state) # 4. 최종 상태 저장

if __name__ == "__main__":
    deploy_all_rules()