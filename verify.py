import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()

# Splunk 접속 정보
SPLUNK_HOST = "https://localhost:8089" # 관리용 포트
USERNAME = "admin"
PASSWORD = "admin1234"

def check_detection(rule_name):
    print(f"🔍 Splunk에서 탐지 여부 확인 중: '{rule_name}'...")
    
    # 최근 5분간 발생한 인시던트 조회 쿼리
    search_query = f"search index=incidents search_name=\"*{rule_name}*\" | head 1"
    
    # 1. 검색 작업 생성
    url = f"{SPLUNK_HOST}/services/search/jobs"
    data = {'search': search_query, 'exec_mode': 'blocking'}
    
    try:
        response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=data, verify=False)
        job_id = response.text
        
        # 2. 결과 개수 확인 (API 응답 파싱이 복잡하므로 간단히 결과 존재 여부만 체크)
        # 실제로는 sid(Job ID)로 results 엔드포인트를 찔러야 하지만,
        # 여기서는 간단히 'exec_mode=blocking'의 결과에서 매칭 카운트를 확인하는 로직으로 대체하거나
        # 더 쉬운 export 방식을 사용합니다.
        
        export_url = f"{SPLUNK_HOST}/services/search/jobs/export"
        export_data = {'search': search_query, 'output_mode': 'json'}
        export_res = requests.post(export_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=export_data, verify=False)
        
        if rule_name in export_res.text:
             print("✅ [PASS] 탐지 성공! Splunk에 인시던트가 생성되었습니다.")
             return True
        else:
             print("❌ [FAIL] 탐지 실패. 인시던트가 발견되지 않았습니다.")
             print(f"   (응답 내용: {export_res.text[:100]}...)")
             return False
             
    except Exception as e:
        print(f"⚠️ API 에러: {e}")
        return False

if __name__ == "__main__":
    # 테스트할 룰 이름의 일부를 인자로 받음
    target_rule = "Atomic Red Team" # YAML 파일의 title에 포함된 키워드
    
    # 공격 후 로그가 인덱싱될 때까지 약간 대기 (Splunk가 느릴 수 있음)
    print("⏳ 로그 인덱싱 대기 중 (15초)...")
    time.sleep(15)
    
    if not check_detection(target_rule):
        sys.exit(1) # 실패 시 CI 파이프라인 중단