import os
import subprocess

# 설정
RULE_DIR = "."  # 룰이 있는 현재 폴더
OUTPUT_FILE = "deploy_queries.txt" # 결과물이 저장될 파일

def run_pipeline():
    print("🚀 [Start] Detection-as-Code Pipeline 시작...")
    
    # 1. 룰 파일 찾기
    yml_files = [f for f in os.listdir(RULE_DIR) if f.endswith('.yml')]
    if not yml_files:
        print("❌ 변환할 YAML 파일이 없습니다.")
        return

    print(f"📦 발견된 룰 파일: {len(yml_files)}개")
    
    with open(OUTPUT_FILE, 'w') as outfile:
        for yml in yml_files:
            print(f"   ⚙️ Converting: {yml} ...", end=" ")
            
            # 2. Sigma CLI 실행 (자동화)
            # 명령어: sigma convert -t splunk --without-pipeline <파일명>
            cmd = ["sigma", "convert", "-t", "splunk", "--without-pipeline", yml]
            
            try:
                # 파이썬에서 터미널 명령어 실행
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                query = result.stdout.strip()
                
                # 3. 결과 저장 (배포용 아티팩트 생성)
                outfile.write(f"### Rule: {yml} ###\n")
                outfile.write(f"{query}\n\n")
                print("✅ 성공")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ 실패 (Error: {e.stderr})")

    print(f"\n✨ [Success] 변환 완료! '{OUTPUT_FILE}' 파일을 확인하세요.")
    print("   (이 파일의 내용을 Splunk Alert에 등록하면 배포가 완료됩니다.)")

if __name__ == "__main__":
    run_pipeline()