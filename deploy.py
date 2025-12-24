def deploy_rule():
    # 1. Sigma(YAML) 파일 읽기
    with open(SIGMA_FILE, 'r') as f:
        rule_content = yaml.safe_load(f)

    # 2. YAML에서 정보 동적 추출
    rule_name = rule_content.get('title', 'Default Title')
    description = rule_content.get('description', 'No Description')
    
    # [핵심] YAML의 detection 필드를 기반으로 쿼리 생성 (단순화 버전)
    # 실제로는 룰마다 쿼리가 다르므로, YAML에 'splunk_query'라는 커스텀 필드를 넣거나 
    # selection의 값을 읽어오도록 로직을 짤 수 있습니다.
    command = rule_content['detection']['selection']['command']
    splunk_query = f'index=* source="/tmp/test.log" "{command}"'

    print(f"🔄 Deploying Rule: {rule_name}")
    print(f"🔍 Generated SPL: {splunk_query}")

    # 3. Payload 자동 구성
    payload = {
        "name": rule_name,
        "search": splunk_query,  # <-- 여기서 자동으로 들어감
        "description": description,
        "alert_type": "number of events",
        "alert_comparator": "greater than",
        "alert_threshold": "0",
        "cron_schedule": "* * * * *",
        "is_scheduled": "1",
        "action.jira_service_desk_simple_addon": "1",
        "action.jira_service_desk_simple_addon.param.account": "rybbit3",
        "action.jira_service_desk_simple_addon.param.project": "SMS",
        "action.jira_service_desk_simple_addon.param.issue_type": "Task"
    }
    
    # ... (이후 API 호출 로직은 동일)