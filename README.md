```markdown
📁 spj010 Project Structure

spj010/
|-- .gitignore           # Git 무시 목록
`-- local
    |-- README.md
    |-- main.py              # Python 실행 스크립트
    |-- pyproject.toml       # Python 의존성 정의
    |-- uv.lock              # Python 의존성 잠금
    |
    |-- .gcp/
    |   `-- .gitkeep         # (GCP .json 키 파일 보관 - Git Ignored)
    |
    |-- envs/
    |   |-- dev.env          # (개발 환경 Secret - Git Ignored)
    |   `-- prod.env         # (운영 환경 Secret - Git Ignored)
    |
    `-- infra/
        |-- main.tf          # 핵심 리소스 정의
        |-- variables.tf     
        |-- outputs.tf       
        |-- .terraform.lock.hcl # (프로바이더 버전 잠금)
        |
        |-- configs/
        |   |-- dev.tfvars   # 개발 환경 설정
        |   `-- prod.tfvars  # 운영 환경 설정
        |
        `-- plans/
            `-- .gitkeep     # (생성된 plan 파일 저장 - Git Ignored)
```
