terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "0.4.0"
    }
  }
}

resource "kind_cluster" "project51_cluster" {
  name       = "project51-dev"
  node_image = "kindest/node:v1.27.1"

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"
    
    # This is the main "master" node
    node {
      role = "control-plane"
      extra_port_mappings {
        container_port = 30080
        host_port      = 8080
        protocol       = "TCP"
      }
    }
    
    # This is your first worker node
    node {
      role = "worker"
    }

    # This is your second worker node
    node {
      role = "worker"
    }
  }
}