# Project51: A Self-Healing AI System with a Resilient CI/CD Pipeline

## 🚀 Introduction

Project51 is a demonstration of a robust, cloud-native application architecture featuring a self-healing AI agent. The core of the project lies not just in the AI's functionality but in the resilient infrastructure and automated pipeline that deploys and maintains it.

This system is designed to be highly available and resilient to failure, leveraging modern DevOps principles and tools. It showcases multiple layers of self-healing, from the application level up to the deployment pipeline.

---

## 🏛️ Architecture Overview

The project is built on a microservices-oriented architecture with a clear separation between the frontend and backend, deployed on a cloud-native infrastructure.

* **Frontend:** A user-facing web application built with **Streamlit**.
* **Backend:** A separate AI agent API, deployed as a managed service on **Render** for stability and ease of management.
* **Cloud Provider:** The entire infrastructure runs on **Amazon Web Services (AWS)**.
* **Compute:** An **EC2 Instance** (`t2.medium`) hosts the Kubernetes cluster.
* **Containerization:** The Streamlit frontend is containerized using **Docker**.
* **Infrastructure as Code (IaC):** The Kubernetes cluster is provisioned and managed declaratively using **Terraform**.
* **Orchestration:** **Kubernetes** (via `kind`) is used to manage and orchestrate the frontend container, providing automated restarts and scaling.
* **CI/CD:** The pipeline is a **CI/CD split**:
    * **Continuous Integration (CI):** A **GitHub Actions** workflow automatically builds the Docker image and pushes it to Docker Hub on every code change.
    * **Continuous Deployment (CD):** A deployment script on the EC2 server pulls the latest image and performs a rolling update on the Kubernetes cluster.

---

## 📁 Project Structure

```plaintext
Project51/
│
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Action for CI (Docker build & push)
│
├── backend/                  # Python code for the backend AI agent (deployed on Render)
│   └── ...
│
├── infra/
│   ├── main.tf               # Terraform script to manage the kind cluster
│   └── kind-config.yaml      # Configuration for the kind cluster
│
├── k8s/
│   ├── deployment.yaml       # Kubernetes manifest for the frontend deployment
│   └── service.yaml          # Kubernetes manifest for the frontend service
│
├── app.py                    # The Streamlit frontend application
├── Dockerfile                # Dockerfile for the Streamlit frontend
├── requirements.txt          # Python dependencies for the frontend
└── deploy.sh                 # Deployment script for the EC2 server (CD)
```

---

## ⚙️ How It Works

### The CI/CD Pipeline

The pipeline is designed for stability, separating the build process (CI) from the deployment process (CD).

#### 1. Continuous Integration (CI)
* A developer pushes a code change to the `main` branch on GitHub.
* This automatically triggers the GitHub Actions workflow defined in `.github/workflows/main.yml`.
* The workflow builds a new Docker image of the Streamlit application.
* Upon a successful build, the image is tagged as `:latest` and pushed to Docker Hub.

#### 2. Continuous Deployment (CD)
* On the EC2 server, a deployment script (`deploy.sh`) is run (either manually or via a cron job).
* The script first pulls the latest code from the GitHub repository to ensure it has the most recent Kubernetes manifests.
* It then runs `kubectl apply -f k8s/` to apply the configuration.
* Crucially, it executes `kubectl rollout restart deployment/...`. This command tells Kubernetes to perform a rolling update, gracefully terminating the old pod and starting a new one. Because the `imagePullPolicy` is set to `Always`, Kubernetes is forced to pull the new `:latest` image from Docker Hub, thus completing the deployment.

---

## 🛠️ Setup and Deployment Guide

Follow these steps to deploy the entire system from scratch.

### Prerequisites
* An **AWS Account** with billing enabled.
* A **GitHub Account**.
* A **Docker Hub Account**.
* **Terraform** and **AWS CLI** installed and configured on your local machine.

### Step-by-Step Instructions

1.  **Deploy Backend:** Deploy the code from the `/backend` folder to a web service on **Render**. Once deployed, copy the public URL of the Render service.

2.  **Configure Frontend:** In `app.py`, update the `API_URL` variable with your live Render URL.

3.  **Launch EC2 Instance:**
    * Launch a new AWS EC2 instance.
    * **Instance Type:** `t2.medium` (important for resource availability).
    * **AMI:** `Ubuntu Server 22.04 LTS`.
    * **Key Pair:** Create and download a new `.pem` key pair.
    * **Security Group:** Create a new security group and add inbound rules to allow traffic on:
        * **Port 22 (SSH)** from your IP.
        * **Port 8080 (TCP)** from Anywhere (`0.0.0.0/0`).

4.  **Set Up Server:**
    * SSH into your new EC2 instance.
    * Install Docker, Terraform, kubectl, and kind using the prerequisite commands.
    * Clone your GitHub repository onto the server: `git clone ...`

5.  **Configure GitHub Secrets:**
    * In your GitHub repository settings, go to `Secrets and variables > Actions`.
    * Add the following secrets:
        * `DOCKER_USERNAME`: Your Docker Hub username.
        * `DOCKER_TOKEN`: Your Docker Hub access token.

6.  **Provision Kubernetes Cluster:**
    * On the EC2 server, navigate to the `infra` directory.
    * Run `terraform init`.
    * Run `terraform apply --auto-approve`. This will create your single-node `kind` cluster.

7.  **Deploy the Application:**
    * Navigate to the project root directory on the EC2 server (`cd ~/Project51`).
    * Run the deployment script: `./deploy.sh`.
    * Check the status with `kubectl get pods -w`. Wait for the pod `STATUS` to become `Running` and `READY` to be `1/1`.

8.  **Access Your Application:**
    * Open your web browser and navigate to `http://<your-ec2-public-ip>:8080`.

---

## ❤️ Self-Healing Mechanisms

This project demonstrates multiple layers of automated self-healing.

1.  **Container-Level Healing:** If the Streamlit process inside the container crashes for any reason, the Docker daemon will automatically restart it based on the restart policy.
2.  **Pod-Level Healing:** The Kubernetes **ReplicaSet** ensures that one replica of your pod is always running. If you manually delete a pod or the node crashes, the ReplicaSet will immediately create a new pod to replace it.
3.  **Deployment-Level Healing:** The `kubectl rollout restart` command in the deployment script ensures a zero-downtime, rolling update. If the new version fails to start, the old, stable version continues to serve traffic.

---

## 🧹 Cleanup

To avoid ongoing AWS charges, follow these steps to destroy all created resources.

1.  **Destroy the Kubernetes Cluster:**
    * SSH into your EC2 instance.
    * Navigate to the `~/Project51/infra` directory.
    * Run `terraform destroy --auto-approve`.

2.  **Terminate the EC2 Instance:**
    * Go to your AWS EC2 Dashboard.
    * Select the instance.
    * Click `Instance state` -> `Terminate instance`.
  



---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

