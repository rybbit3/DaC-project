import requests
import yaml
import sys
import urllib3

# SSL 경고 무시 (로컬 인증서 때문)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 설정 =================
SPLUNK_URL = "https://localhost:8089"  # 관리 포트
USERNAME = "admin"
PASSWORD = "admin1234"  # Docker 실행 시 설정한 비번
SIGMA_FILE = "rules/detect_whoami.yml" # 배포할 룰 파일 경로
# =======================================

def deploy_rule():
    # 1. Sigma(YAML) 파일 읽기
    print(f"📂 Reading rule file: {SIGMA_FILE}...")
    with open(SIGMA_FILE, 'r') as f:
        rule_content = yaml.safe_load(f)

    # 2. 필요한 정보 추출 (시나리오 -> 설정값)
    rule_name = rule_content['title']
    description = rule_content['description']
    
    # 원래는 여기서 'sigmatools'로 자동 변환해야 하지만, 
    # 실습의 단순화를 위해 변환된 SPL을 직접 정의하겠습니다.
    # (이전 실습 결과물)
    splunk_query = 'index=linux CommandLine="*whoami*"' 

    print(f"🔄 Converting to SPL: {splunk_query}")

    # 3. Splunk API에 쏘기 (여기가 핵심!)
    # Endpoint: Saved Search를 생성하는 주소
    api_endpoint = f"{SPLUNK_URL}/servicesNS/admin/search/saved/searches"
    
    payload = {
        "name": rule_name,              # 룰 이름
        "search": splunk_query,         # 변환된 쿼리 (SPL)
        "description": description,     # 설명
        "is_visible": "1",              # 메뉴에서 보이게 설정
        "alert_type": "number of events",
        "alert_comparator": "greater than",
        "alert_threshold": "0",         # 1건이라도 탐지되면 경보
        "cron_schedule": "* * * * *",   # 1분마다 실행 (실시간 감시 흉내)
        "is_scheduled": "1"             # 스케줄 활성화
    }

    try:
        response = requests.post(
            api_endpoint, 
            data=payload, 
            auth=(USERNAME, PASSWORD), 
            verify=False # 로컬이라 SSL 검증 끔
        )

        if response.status_code == 201: # 생성 성공
            print(f"✅ [SUCCESS] Rule '{rule_name}' successfully deployed to Splunk!")
        elif response.status_code == 409: # 이미 있음
            print(f"⚠️ [EXISTS] Rule '{rule_name}' already exists. (Consider update logic)")
        else:
            print(f"❌ [FAIL] Error: {response.text}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    deploy_rule()