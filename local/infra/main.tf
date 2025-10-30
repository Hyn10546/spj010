# SAMPLE

# Terraform 실행에 필요한 Provider 버전을 명시합니다.
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # 원하는 버전 명시
    }
  }
}

# Google Provider 설정
# project, region, zone 값은 variables.tf를 통해 자동으로 주입됩니다.
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
  # GOOGLE_APPLICATION_CREDENTIALS 환경 변수는
  # provider가 자동으로 읽어가므로 여기에 명시할 필요가 없습니다.
}

# --- 예시: "hello-world" GCE VM 인스턴스 생성 ---
resource "google_compute_instance" "default" {
  name         = "hello-world-vm"
  machine_type = "e2-micro"
  zone         = var.zone # variables.tf에서 받은 zone 값 사용

  # 부팅 디스크 설정
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  # 네트워크 설정
  network_interface {
    network = "default"
    access_config {
      # 빈 access_config 블록은 임시 외부 IP를 할당합니다.
    }
  }
}