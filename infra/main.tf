# terraform {
#   required_providers {
#     kind = {
#       source  = "tehcyx/kind"
#       version = "0.4.0"
#     }
#   }
# }

# resource "kind_cluster" "project51_cluster" {
#   name       = "project51-dev"
#   node_image = "kindest/node:v1.27.1"

#   kind_config {
#     kind        = "Cluster"
#     api_version = "kind.x-k8s.io/v1alpha4"
    
#     # This is the main "master" node
#     node {
#       role = "control-plane"
#       extra_port_mappings {
#         container_port = 30080
#         host_port      = 8080
#         protocol       = "TCP"
#       }
#     }
    
#     # This is your first worker node
#     node {
#       role = "worker"
#     }

#     # This is your second worker node
#     node {
#       role = "worker"
#     }
#   }
# }




terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "3.2.2"
    }
  }
}

# This resource uses Terraform to manage the lifecycle of your kind cluster
resource "null_resource" "kind_cluster" {

  # This trigger ensures that if the config file changes, Terraform will recreate the cluster
  triggers = {
    config_hash = filemd5("kind-config.yaml")
  }

  # On 'terraform apply', run the kind create command
  provisioner "local-exec" {
    command = "kind create cluster --name project51-dev --config kind-config.yaml"
  }

  # On 'terraform destroy', run the kind delete command
  provisioner "local-exec" {
    when    = destroy
    command = "kind delete cluster --name project51-dev"
  }
}