import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()

SPLUNK_HOST = "https://localhost:8089"
USERNAME = "admin"
PASSWORD = "admin1234"

def check_detection_with_retry(rule_name, max_retries=12, interval=10):
    print(f"🔍 Splunk 탐지 확인 시작: '{rule_name}' (최대 {max_retries*interval}초 대기)")
    
    search_query = f"search index=incidents search_name=\"*{rule_name}*\" | head 1"
    url = f"{SPLUNK_HOST}/services/search/jobs/export"
    data = {'search': search_query, 'output_mode': 'json'}
    
    for i in range(max_retries):
        try:
            response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=data, verify=False)
            
            # 결과에 룰 이름이 포함되어 있으면 성공
            if rule_name in response.text:
                print(f"✅ [PASS] 탐지 성공! ({i*interval}초 소요)")
                return True
            else:
                print(f"⏳ ({i+1}/{max_retries}) 아직 탐지 안 됨... 스케줄러 대기 중")
                
        except Exception as e:
            print(f"⚠️ API 에러: {e}")
            
        time.sleep(interval)
        
    print("❌ [FAIL] 시간 초과! 인시던트가 생성되지 않았습니다.")
    return False

if __name__ == "__main__":
    target_rule = "Atomic Red Team" # YAML 룰의 제목 키워드
    
    if not check_detection_with_retry(target_rule):
        sys.exit(1)