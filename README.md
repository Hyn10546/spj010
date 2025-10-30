```markdown
### 📁 Project Structure

```plaintext
spj010/
`-- local
    |-- README.md
    |-- .gitignore           # Git 무시 목록 (중요)
    |-- main.py              # Python 실행 스크립트
    |-- pyproject.toml       # Python 의존성 정의
    |-- uv.lock              # Python 의존성 잠금
    |
    |-- .gcp/
    |   `-- .gitkeep         # (GCP .json 키 파일을 여기에 보관 - Git 무시됨)
    |
    |-- envs/
    |   |-- .gitkeep
    |   |-- dev.env          # (개발 환경 비밀 - Git 무시됨)
    |   `-- prod.env         # (운영 환경 비밀 - Git 무시됨)
    |
    `-- infra/
        |-- main.tf          # 핵심 리소스 정의
        |-- variables.tf     # (variable.tf -> variables.tf로 수정 권장)
        |-- outputs.tf       # (output.tf -> outputs.tf로 수정 권장)
        |-- .terraform.lock.hcl # (프로바이더 버전 잠금 - Git에 커밋)
        |
        |-- configs/
        |   |-- dev.tfvars   # 개발 환경 설정 (Git에 커밋)
        |   `-- prod.tfvars  # 운영 환경 설정 (Git에 커밋)
        |
        `-- plans/
            `-- .gitkeep     # (생성된 plan 파일 저장 - Git 무시됨)
