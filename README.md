# DaC-project

## 개요

1. 배경 (Background)
기존의 SIEM 운영 환경에서는 탐지 룰을 수동으로 등록하고, 공격이 발생한 뒤에야 룰이 정상 동작하는지 알 수 있는 문제가 있었습니다. 이를 해결하기 위해 소프트웨어 개발 수명주기(SDLC) 방식을 보안 운영에 도입했습니다.

2. 목표 (Goal)
표준화: Sigma(YAML)를 이용해 룰 포맷을 통일하고 버전 관리(Git)를 적용.

자동화: Github Actions를 통해 룰 변환(Build) 및 배포(Deploy) 자동화.

신뢰성: 실제 공격 시뮬레이션(BAS)을 통해 룰의 유효성을 배포 즉시 검증(Test).

## 아키텍처

Self-Hosted Runner를 활용하여 로컬 Docker 환경과 Github Cloud를 연동한 하이브리드 CI/CD 구조입니다.

## 기술 스택
- Core: Detection-as-Code (DaC)
- Rule Engine: Sigma (Generic Signature Format)
- CI/CD: Github Actions (Self-Hosted Runner on macOS)
- SIEM: Splunk Enterprise (Docker Container)
- Attack Simulation: Atomic Red Team (T1059.001 PowerShell)
- Scripting: Python (Build/Verify), PowerShell (Attack), Bash

## 주요 기능 (Key Features)

1. Automated Build (Sigma to Splunk)
pipeline.py 스크립트가 rules/ 폴더 내의 YAML 파일들을 파싱합니다.

Sigma CLI를 호출하여 Splunk SPL(Search Processing Language)로 변환합니다.

Splunk가 인식할 수 있는 savedsearches.conf 설정 파일을 자동으로 생성합니다.

2. Seamless Deployment (Docker Integration)
생성된 설정 파일을 Docker 컨테이너(my-splunk-lab) 내부의 로컬 앱 경로로 전송합니다.

Splunk REST API를 통해 설정을 리로드(Reload)하여, 재시작 없이 즉시 정책을 반영합니다.

3. Attack Simulation (Atomic Red Team)
배포 직후, Atomic Red Team을 사용하여 실제 공격(T1059.001 - PowerShell Execution)을 수행합니다.

가짜 로그 주입이 아닌, 실제 프로세스 실행을 통해 EDR/SIEM 관점의 실전 테스트를 수행합니다.

4. Closed-Loop Verification
verify.py가 Splunk API(8089 포트)에 접속하여 방금 실행한 공격이 index=incidents에 경보로 기록되었는지 확인합니다.

탐지 실패 시 파이프라인을 Fail 처리하여 배포 안정성을 보장합니다.

test