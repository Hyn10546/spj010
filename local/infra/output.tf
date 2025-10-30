# SAMPLE

output "vm_name" {
  description = "생성된 VM 인스턴스의 이름"
  value       = google_compute_instance.default.name
}

output "vm_external_ip" {
  description = "생성된 VM 인스턴스의 외부 IP 주소"
  value       = google_compute_instance.default.network_interface[0].access_config[0].nat_ip
}