import subprocess
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv


# --- 1. Helper Function: User Confirmation ---
def ask_for_confirmation(prompt_message):
    """
    사용자에게 'yes' 또는 'no' 입력을 받아 True/False를 반환합니다.
    """
    while True:
        response = input(prompt_message).lower().strip()
        if response == 'yes':
            return True
        if response == 'no':
            return False
        print(">>> 'yes' 또는 'no'로만 입력해주세요.")
        
# --- 2. Helper Function: Command Execution ---

def run_terraform_command(command_list, stage, terraform_dir):
    """
    주어진 command_list를 'terraform_dir' 디렉터리에서 실행합니다.
    """
    print(f"--- {terraform_dir} (stage: {stage})에서 실행 중: {' '.join(command_list)} ---")
    
    # Popen은 기본적으로 부모 프로세스(이 스크립트)의 환경 변수를 상속받습니다.
    # load_dotenv()가 os.environ에 로드한 변수들이 그대로 전달됩니다.
    with subprocess.Popen(
        command_list,
        cwd=terraform_dir, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True, 
        encoding='utf-8',
        bufsize=1
    ) as process:
        
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='') # 실시간 출력 & 줄바꿈 문자가 포함되어 있으므로 end='' 사용

    if process.returncode != 0:
        print(f"--- 오류 발생: {' '.join(command_list)} (종료 코드: {process.returncode}) ---", file=sys.stderr)
        return False # 실패 시 False 반환
    
    print(f"--- 완료: {' '.join(command_list)} ---")
    return True # 성공 시 True 반환

# --- 3. Helper Function: Run Plan ---

def run_plan(stage, terraform_dir):
    """
    Terraform Plan을 실행하고 저장된 plan 파일 경로를 반환합니다.
    실패 시 None을 반환합니다.
    """
    print(f"--- '{stage}' 환경에 대한 Plan을 생성합니다... ---")
    
    CONFIGS_SUBDIR = "configs"
    PLANS_SUBDIR = "plans"
    
    # 'infra/plans' 디렉터리 생성
    full_plans_dir_path = os.path.join(terraform_dir, PLANS_SUBDIR)
    os.makedirs(full_plans_dir_path, exist_ok=True)
    
    # .tfvars 파일 경로 (예: "configs/dev.tfvars")
    tfvars_file = os.path.join(CONFIGS_SUBDIR, f"{stage}.tfvars")
    
    # .tfplan 파일 경로 (예: "plans/dev_20251030_140000.tfplan")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file_name = f"{stage}_{timestamp}.tfplan"
    plan_file_rel_path = os.path.join(PLANS_SUBDIR, plan_file_name)
    
    plan_command = [
        'terraform', 
        'plan', 
        f'-var-file={tfvars_file}',
        f'-out={plan_file_rel_path}'
    ]
    
    if run_terraform_command(plan_command, stage, terraform_dir):
        print(f"^v^ Plan 파일 저장 완료: {terraform_dir}/{plan_file_rel_path}")
        return plan_file_rel_path # 성공 시 plan 파일 경로 반환
    else:
        print("Terraform plan 실패.", file=sys.stderr)
        return None # 실패 시 None 반환

# --- 4. Action Functions ---

def action_plan(stage, terraform_dir):
    """'plan' 작업을 수행합니다."""
    run_plan(stage, terraform_dir)

def action_apply(stage, terraform_dir):
    """'apply' 작업을 수행합니다."""
    # 1. Plan 실행
    plan_file_rel_path = run_plan(stage, terraform_dir)
    
    if not plan_file_rel_path:
        return # Plan 실패 시 중단

    # 2. 사용자 확인
    print("\n" + "="*50)
    print(f"^v^ Terraform Plan이 'infra/{plan_file_rel_path}'로 저장되었습니다.")
    print("="*50)
    
    prompt = f"^v^ '{stage}' 환경에 이 계획을 적용하시겠습니까? (yes/no): "
    
    if ask_for_confirmation(prompt):
        print(f"--- 사용자가 'yes'를 입력했습니다. '{plan_file_rel_path}'을 적용합니다. ---")
        
        # 3. Apply 실행
        apply_command = ['terraform', 'apply', plan_file_rel_path]
        
        if not run_terraform_command(apply_command, stage, terraform_dir):
            print("Terraform apply 실패.", file=sys.stderr)
            return
    else:
        print("--- 사용자가 'no'를 입력했습니다. 작업을 취소합니다. ---")

def action_destroy(stage, terraform_dir):
    """'destroy' 작업을 수행합니다."""
    print(f"--- '{stage}' 환경에 대한 파괴(Destroy) 작업을 시작합니다. ---")
    
    CONFIGS_SUBDIR = "configs"
    tfvars_file = os.path.join(CONFIGS_SUBDIR, f"{stage}.tfvars")

    # 1. [중요] 파괴 작업에 대한 강력한 확인
    print("\n" + "="*50)
    print(f"^v^ 경고: '{stage}' 환경의 모든 Terraform 리소스를 파괴합니다.")
    print("="*50)
    
    prompt = f"^v^ '{stage}' 환경을 정말로 파괴하시겠습니까? (yes/no): "

    if ask_for_confirmation(prompt):
        print(f"--- 사용자가 'yes'를 입력했습니다. '{stage}' 환경 파괴를 시작합니다. ---")
        
        # 2. Destroy 실행 (-auto-approve 사용)
        destroy_command = [
            'terraform',
            'destroy',
            f'-var-file={tfvars_file}',
            '-auto-approve'
        ]
        
        if not run_terraform_command(destroy_command, stage, terraform_dir):
            print("Terraform destroy 실패.", file=sys.stderr)
            return
    else:
        print("--- 사용자가 'no'를 입력했습니다. 파괴 작업을 취소합니다. ---")

# --- 5. Main Execution ---

def main():
    # 1. Argument Parser 설정 (Sub-parser 사용)
    parser = argparse.ArgumentParser(description="Run Terraform for a specific stage.")
    
    # 전역 인수 (모든 하위 명령에 적용)
    parser.add_argument(
        "--stage", 
        type=str, 
        required=True, 
        choices=['dev', 'prod'], # 허용할 스테이지 목록
        help="The environment stage (e.g., dev, prod)"
    )
    
    # 하위 명령(sub-command) 설정
    # 하위 명령(sub-command) 설정
    subparsers = parser.add_subparsers(
        dest="action", 
        required=True, 
        help="Action to perform: plan, apply, or destroy"
    )
    
    # 'plan' 명령
    subparsers.add_parser("plan", help="Generate and save an execution plan.")
    
    # 'apply' 명령
    subparsers.add_parser("apply", help="Generate a plan, ask for confirmation, and apply.")
    
    # 'destroy' 명령
    subparsers.add_parser("destroy", help="Ask for confirmation and destroy resources.")

    args = parser.parse_args()
    stage = args.stage # 예: 'dev' 또는 'prod'
    action = args.action  
    
    # 2. .env 파일 로드 
    env_file_path = os.path.join("envs", f"{stage}.env")

    if not os.path.exists(env_file_path):
        print(f"오류: {env_file_path} 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
        
    load_dotenv(env_file_path)
    print(f"✅ {env_file_path} (비밀) 로드 완료.")
    
    # --- 상대 경로를 절대 경로로 변환 ---
    # Terraform이 cwd='infra'에서 실행될 때 상대 경로 문제를 해결하기 위함
    gcp_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds_path and not os.path.isabs(gcp_creds_path):
        # 현재 .env에 적힌 경로가 상대 경로라면,
        # main.py 실행 위치(루트)를 기준으로 절대 경로를 생성합니다.
        abs_path = os.path.abspath(gcp_creds_path)
        
        # [핵심] 환경 변수 값을 "절대 경로"로 덮어씁니다.
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
    
    # 3. Terraform 워크플로우 실행
    
    # 3.1. Terraform Init (모든 작업의 공통)
    init_command = ['terraform', 'init']
    TERRAFORM_DIR = "infra"
    
    if not run_terraform_command(init_command, stage, TERRAFORM_DIR):
        print("Terraform init 실패. 스크립트를 중단합니다.", file=sys.stderr)
        return

    # 3.2. 선택된 Action에 따라 분기
    if action == "plan":
        action_plan(stage, TERRAFORM_DIR)
    elif action == "apply":
        action_apply(stage, TERRAFORM_DIR)
    elif action == "destroy":
        action_destroy(stage, TERRAFORM_DIR)
    
    print(f"\n🎉 '{stage}' 환경 '{action}' 작업이 완료되었습니다.")


if __name__ == "__main__":
    main()