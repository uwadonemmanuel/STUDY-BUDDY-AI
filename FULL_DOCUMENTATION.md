### 1. Initial Setup

- **Push code to GitHub**  
  Push your project code to a GitHub repository.

- **Create a Dockerfile**  
  Write a `Dockerfile` in the root of your project to containerize the app.

- **Create Kubernetes Manifest Directory**  
  Make a directory named `manifests/` to store all Kubernetes deployment YAML files.

- **Create a VM Instance on Google Cloud**

  - Go to VM Instances and click **"Create Instance"**
  - Name: `gitops`
  - Machine Type:
    - Series: `E2`
    - Preset: `Standard`
    - Memory: `16 GB RAM`
  - Boot Disk:
    - Change size to `256 GB`
    - Image: Select **Ubuntu 24.04 LTS**
  - Networking:
    - Enable HTTP and HTTPS traffic

- **Create the Instance**

- **Connect to the VM**
  - Use the **SSH** option provided to connect to the VM from the browser.



### 2. Configure VM Instance

- **Clone your GitHub repo**

  ```bash
  git clone https://github.com/data-guru0/TESTING-9.git
  ls
  cd TESTING-9
  ls  # You should see the contents of your project
  ```

- **Install Docker**

  - Search: "Install Docker on Ubuntu"
  - Open the first official Docker website (docs.docker.com)
  - Scroll down and copy the **first big command block** and paste into your VM terminal
  - Then copy and paste the **second command block**
  - Then run the **third command** to test Docker:

    ```bash
    docker run hello-world
    ```

- **Run Docker without sudo**

  - On the same page, scroll to: **"Post-installation steps for Linux"**
  - Paste all 4 commands one by one to allow Docker without `sudo`
  - Last command is for testing

- **Enable Docker to start on boot**

  - On the same page, scroll down to: **"Configure Docker to start on boot"**
  - Copy and paste the command block (2 commands):

    ```bash
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    ```

- **Verify Docker Setup**

  ```bash
  systemctl status docker       # You should see "active (running)"
  docker ps                     # No container should be running
  docker ps -a                 # Should show "hello-world" exited container
  ```


### 3. Configure Minikube inside VM

- **Install Minikube**

  - Open browser and search: `Install Minikube`
  - Open the first official site (minikube.sigs.k8s.io) with `minikube start` on it
  - Choose:
    - **OS:** Linux
    - **Architecture:** *x86*
    - Select **Binary download**
  - Reminder: You have already done this on Windows, so you're familiar with how Minikube works

- **Install Minikube Binary on VM**

  - Copy and paste the installation commands from the website into your VM terminal

- **Start Minikube Cluster**

  ```bash
  minikube start
  ```

  - This uses Docker internally, which is why Docker was installed first

- **Install kubectl**

  - Search: `Install kubectl`
  - Run the first command with `curl` from the official Kubernetes docs
  - Run the second command to validate the download
  - Instead of installing manually, go to the **Snap section** (below on the same page)

  ```bash
  sudo snap install kubectl --classic
  ```

  - Verify installation:

    ```bash
    kubectl version --client
    ```

- **Check Minikube Status**

  ```bash
  minikube status         # Should show all components running
  kubectl get nodes       # Should show minikube node
  kubectl cluster-info    # Cluster info
  docker ps               # Minikube container should be running
  ```


### 4. Jenkins Setup

- **Run Jenkins in Docker (DIND Mode)**

  - First, check existing networks:

    ```bash
    docker network ls
    ```

  - Ensure Jenkins runs on the **same Docker network** as Minikube.

  - Run Jenkins container:

    ```bash
    docker run -d --name jenkins \
    -p 8080:8080 \
    -p 50000:50000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(which docker):/usr/bin/docker \
    -u root \
    -e DOCKER_GID=$(getent group docker | cut -d: -f3) \
    --network minikube \
    jenkins/jenkins:lts
    ```

- **Verify Jenkins Container**

  ```bash
  docker ps                  # Jenkins container should be running
  docker logs jenkins        # Copy the admin password shown here
  ```

- **Access Jenkins Web UI**

  - Go to your VM dashboard in GCP
  - Copy the **External IP (public DNS)** and open:  
    `http://<EXTERNAL_IP>:8080`

  - If the page doesn't load, set a **firewall rule**:

    - GCP → VPC Network → Firewall → **Create Firewall Rule**
      - Name: `allow-jenkins`
      - Description: Allow all traffic (for Jenkins demo)
      - Logs: Off
      - Network: `default`
      - Direction: `ingress`
      - Action: `allow`
      - Targets: `All instances`
      - Source IP ranges: `0.0.0.0/0`
      - Allowed protocols and ports: `all`

- **Jenkins Setup Steps**

  - Paste the initial password from `docker logs jenkins`
  - Click **Install Suggested Plugins**
  - Create Admin User
  - Skip agent security warning (ignore for now)

- **Install Required Plugins**

  - Navigate to: **Manage Jenkins → Plugins**
    - Install:
      - Docker
      - Docker Pipeline
      - Kubernetes

- **Restart Jenkins**

  ```bash
  docker restart jenkins
  ```

  - Log in again after restart

- **Install Python and Pip inside Jenkins Container**

  ```bash
  docker exec -it jenkins bash
  apt update -y
  apt install -y python3
  python3 --version
  ln -s /usr/bin/python3 /usr/bin/python
  python --version
  apt install -y python3-pip
  apt install -y python3-venv
  exit
  ```

- **Restart Jenkins Again**

  ```bash
  docker restart jenkins
  ```

✅ Jenkins is now fully set up and ready to use!

### 5. GitHub Integration with Jenkins

---

#### 🔐 Generate GitHub Personal Access Token

- Go to: **GitHub → Settings → Developer Settings → Personal access tokens → Generate new token**
- Select **classic token** and give it the following permissions:

  ```
  admin:org
  admin:org_hook
  admin:public_key
  admin:repo_hook
  repo
  workflow
  ```

---

#### 🔑 Add GitHub Credentials to Jenkins

- Go to: **Manage Jenkins → Credentials → Global → Add Credentials**
  - **Username**: Your GitHub username
  - **Password**: The token you just generated
  - **ID**: `github-token`
  - **Description**: `github-token`

---

#### 🚀 Create a New Pipeline Job in Jenkins

1. Go to Jenkins Dashboard → **New Item**
2. Enter **Name**: `gitops`
3. Select **Pipeline**
4. Scroll to the **Pipeline** section:
   - Select **Pipeline from SCM**
   - Choose **Git**
   - **Repository URL**: Your GitHub repo link
   - **Credentials**: Select the `github-token` credential
   - **Branch**: `main`

---

#### 🧱 Create Jenkinsfile in VM

- Open **Pipeline Syntax Generator** in a new tab (for reference)
- On your VM terminal:

  ```bash
  vi Jenkinsfile
  ```

- Paste the following Jenkins pipeline code:

  ```groovy
  pipeline {
      agent any
      stages {
          stage('Checkout Github') {
              steps {
                  echo 'Checking out code from GitHub...'
                  checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/data-guru0/GitOPS-testing.git']])
              }
          }        
          stage('Build Docker Image') {
              steps {
                  echo 'Building Docker image...'
              }
          }
          stage('Push Image to DockerHub') {
              steps {
                  echo 'Pushing Docker image to DockerHub...'
              }
          }
          stage('Install Kubectl & ArgoCD CLI') {
              steps {
                  echo 'Installing Kubectl and ArgoCD CLI...'
              }
          }
          stage('Apply Kubernetes & Sync App with ArgoCD') {
              steps {
                  echo 'Applying Kubernetes and syncing with ArgoCD...'
              }
          }
      }
  }
  ```

- Save and exit:
  
  - Press `Esc`, then type `:wq!` and hit `Enter`

---

#### 🔃 Push Jenkinsfile to GitHub

```bash
git config --global user.email "uwadonemmanuel@gmail.com"
git config --global user.name "data-guru0"

git add .
git commit -m "commit"
git push origin main
```

- When prompted:
  - **Username**: `data-guru0`
  - **Password**: GitHub token (paste, it's invisible)

---

#### ✅ Final Jenkins Test

- Go back to Jenkins Dashboard
- Click on your `gitops` pipeline
- Click **Build Now**

If successful ✅, GitHub is now **fully integrated** with Jenkins!

---

### 6. Build and Push Docker Image to DockerHub

---

#### ⚙️ Configure Docker Tool in Jenkins

1. Go to **Jenkins Dashboard → Manage Jenkins → Tools**
2. Scroll down to **Docker Installations**
3. Click **Add Docker**
   - **Name**: `Docker`
   - ✅ Check **Install automatically**
   - Select **Install from docker.com**
4. Click **Apply and Save**

---

#### 💻 Sync Local Code from GitHub

In VS Code terminal:

```bash
git pull origin main
```

---

#### 🐳 Create DockerHub Repository

1. Go to [https://hub.docker.com](https://hub.docker.com)
2. Create a new repository, e.g., `uwadonemmanuel/testing-9`

---

#### 🔐 Generate DockerHub Access Token

1. Go to **DockerHub Account → Account Settings → Security → New Access Token**
2. Name it appropriately and give it **Read/Write** permission
3. Copy the generated token

---

#### ➕ Add DockerHub Credentials to Jenkins

1. Go to **Jenkins → Manage Jenkins → Credentials → Global → Add Credentials**
   - **Username**: DockerHub username (e.g., `uwadonemmanuel`)
   - **Password**: The DockerHub token
   - **ID**: `gitops-dockerhub`
   - **Description**: `DockerHub Access Token`

---

#### 🧱 Update `Jenkinsfile` in VS Code

Add an `environment` block at the top of the pipeline:

Update the `Build Docker Image` and `Push Image to DockerHub` stages like given in Jenkinsfile in repo

---

#### 🔁 Push Changes to GitHub

```bash
git add .
git commit -m "Add Docker build and push stages"
git push origin main
```

---

#### 🚀 Trigger Jenkins Pipeline

1. Go to Jenkins Dashboard
2. Click on your pipeline (`gitops`)
3. Click **Build Now**

✅ If successful, your image will be available on DockerHub:  
`https://hub.docker.com/r/uwadonemmanuel/testing-9`

---


### 7. Install and Configure ArgoCD - Part 1

---

#### 🧾 Step 1: Check Existing Namespaces

```bash
kubectl get namespace
```

---

#### 🆕 Step 2: Create New Namespace for ArgoCD

```bash
kubectl create ns argocd
```

✅ Run the first command again to verify the namespace is created.

---

#### 📦 Step 3: Install ArgoCD

Apply the ArgoCD installation manifest from GitHub:

```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

---

#### 🔍 Step 4: Validate ArgoCD Components

Check all resources inside the `argocd` namespace:

```bash
kubectl get all -n argocd
```

✅ Wait until all resources (pods, deployments, replicasets, etc.) are in **Running** or **Completed** state.  
⛔ Do **not proceed** if anything is in **Pending** or **CrashLoopBackOff** state.

---

#### 🔌 Step 5: Check ArgoCD Service Type

```bash
kubectl get svc -n argocd
```

You’ll notice that `argocd-server` is of type **ClusterIP**, which is only accessible within the cluster.

We need to change it to **NodePort** to access the UI externally.

---

#### 🔧 Step 6: Change ClusterIP to NodePort

Edit the service:

```bash
kubectl edit svc argocd-server -n argocd
```

- Find: `type: ClusterIP`
- Replace with: `type: NodePort`

Then press:
- `Ctrl + X` → `Y` → `Enter` (or `:wq!` if in Vim)

Now re-run:

```bash
kubectl get svc -n argocd
```

✅ You will now see `argocd-server` with a **NodePort**, such as `31704`.

---

#### 🌐 Step 7: Access ArgoCD UI in Browser

Open a **new SSH terminal** and run:

```bash
kubectl port-forward --address 0.0.0.0 service/argocd-server 31704:80 -n argocd
```

- Now open your browser
- Enter: `http://<VM_PUBLIC_IP>:31704`
- You may see a privacy warning—proceed anyway

✅ You’ll land on the ArgoCD **login page**

---

#### 🔐 Step 8: Get ArgoCD Admin Password

Open another terminal and run:

```bash
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

- **Username**: `admin`
- **Password**: (copy from above)

Login and you’re now inside the ArgoCD UI 🎉

---

### 8. Install and Configure ArgoCD – Part 2

---

#### ⚙️ Step 1: Locate Your Kubernetes Config File ( Already given this file in Course Materials Download from there )



Go to the root directory:

```bash
cd ~
ls -la
```

You’ll see a hidden directory `.kube/` — this stores your Kubernetes configuration.

Check the content:

```bash
ls -la .kube/
cat .kube/config
```

Copy the entire content of `.kube/config` into a Notepad for backup and modification.

---

#### 🔐 Step 2: Convert File Paths to Base64 Encoded Strings

The `config` file references files like:

- `/home/gyrogodnon/.minikube/ca.crt`
- `/home/gyrogodnon/.minikube/profiles/minikube/client.crt`
- `/home/gyrogodnon/.minikube/profiles/minikube/client.key`

We’ll **inline** the actual base64 content instead of using file paths.

##### 🔁 For Each of These 3 Files, Run:

```bash
cat /home/gyrogodnon/.minikube/ca.crt | base64 -w 0; echo
cat /home/gyrogodnon/.minikube/profiles/minikube/client.crt | base64 -w 0; echo
cat /home/gyrogodnon/.minikube/profiles/minikube/client.key | base64 -w 0; echo
```

Copy each base64 string and replace the corresponding `certificate-authority-data`, `client-certificate-data`, and `client-key-data` fields in your config file. *** But remember to change `certificate-authority` to `certificate-authority-data`, `client-certificate` to `client-certificate-data`, and `client-key` to `client-key-data`

---

#### 📝 Step 3: Save Edited Kubeconfig File

- Save this new file as `kubeconfig` (no `.txt` extension) in your **Downloads** folder.

Now open Git Bash and run:

```bash
cd ~/Downloads
vi config
```

Paste the full edited config content.

Save it:

- Press `Esc`, then type `:wq!` and hit Enter.

---

#### 🔒 Step 4: Add kubeconfig as Secret File in Jenkins

- Go to **Jenkins Dashboard → Manage Jenkins → Credentials**
- Select: **Global → Add Credentials**
- Choose: **Kind: Secret file**
- Upload your edited `config` file
- Set:
  - **ID**: `kubeconfig`
  - **Description**: `kubeconfig`

Click Save ✅

---

#### ☁️ Step 5: Set Up Kubernetes Cluster Access in Jenkins Pipeline

1. Go to Jenkins Dashboard → Pipelines → Open your `GitOps` pipeline
2. Click **Configure**
3. Scroll down to **Pipeline section**
4. Click **Pipeline Syntax** → Opens in a new tab
5. Select:
   - **Sample Step**: `kubernetes deploy`
   - **Kubeconfig**: select `kubeconfig` credential
   - **Server URL**: Get from this command:
     ```bash
     kubectl cluster-info
     ```
     (e.g., `https://192.168.49.2:8443`)
6. Generate the script

Copy the generated script and paste/save it — you’ll use it in your Jenkinsfile in the next stage.

---

✅ At this point, your Jenkins instance is fully connected to your Kubernetes cluster using a secure kubeconfig setup.

---

# 9. Install and Configure ArgoCd - Part 3


### Step 1: Install `kubectl` and ArgoCD CLI on Docker Container

- Open **VS Code** and navigate to your **Jenkinsfile**.
- Copy-paste the code snippet you have for installing **ArgoCD** and **kubectl**.
- This snippet will be used in the pipeline.

---

### Step 2: Apply Kubernetes & Sync App with ArgoCD Stage

- Inside the pipeline stage, create a script block.
- Paste the copied installation commands inside the script.
- Replace the placeholder IP address with your **own ArgoCD server IP**.
  
```groovy
sh '''
argocd login 34.72.5.170:31704 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
'''
````

> **Note:** Change `34.72.5.170:31704` to your ArgoCD server IP and port.

---

### Step 3: Connect GitHub Repository to ArgoCD

1. Open **ArgoCD UI** → Go to **Settings** → **Repositories** → **Connect Repo** via HTTPS.
2. Fill in details:

   * **Type:** git
   * **Name:** anything you want
   * **Project:** default
   * **Repo URL:** `https://github.com/data-guru0/GitOPS-testing.git`
   * **Username & Password:** Provide GitHub username and token (optional but recommended)
3. Click **Connect**.
4. You should see a success message confirming the GitHub repo is connected to ArgoCD.

---

### Important:

```bash
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="your-groq-api-key" \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  -n argocd
```

### Step 4: Create a New Application in ArgoCD

* Go to **Applications** → Click **New App**.
* Fill in the form:

  * **Name:** Gitops (or any name you prefer)
  * **Project:** default
  * **Sync Policy:** Automatic
  * Tick **Sync Pipeline Resources** and **Self Heal**.
  * Leave other settings as default.
  * **Repository URL:** select your connected repo.
  * **Revision:** `main` (branch)
  * **Path:** `manifests`
  * **Cluster URL:** select from dropdown.
  * **Namespace:** `argocd`
* Click **Create**.
* You should see the application status as **Synced** and **Healthy**.

---

### Step 5: Modify Jenkinsfile to Sync ArgoCD Application

* In **VS Code**, open your `Jenkinsfile`.
* In the last stage, add the command to sync the ArgoCD app:

```groovy
sh 'argocd app sync gitopsapp'
```

> Replace `gitopsapp` with the actual name of your ArgoCD application.

* Push the changes to GitHub.
* Go to Jenkins and build the pipeline.
* On success, you will see a success message.

---

### Step 6: Verify ArgoCD Application and Logs

* Open **ArgoCD UI**.
* Check the application workflow.
* View logs for each pod to verify deployment.

---

### Step 7: Access Your Application

* On your VM instance terminal, run:

```bash
kubectl get deploy -n argocd
```

* You should see your `mlops-app` deployment.
* Check pods:

```bash
kubectl get pods -n argocd
```

* You should see your pods running.

---

### Step 8: Allow External Access

* Run the following command to create a tunnel:

```bash
minikube tunnel
```

* Open another SSH terminal and run port-forwarding:

```bash
kubectl port-forward svc/my-service -n argocd --address 0.0.0.0 9090:80
```
Replace my-service with the name in the manifests/service.yaml

---

### Step 9: Access the Application from Browser

* Copy your VM’s external IP address.
* Open browser and go to:

```
http://<VM_EXTERNAL_IP>:9090
```

* You should see your `mlops-app` running successfully!


# 10. Setup Webhooks

---

### Step 1: Add Webhook in GitHub Repository

1. Go to your **GitHub repo** → **Settings** → **Webhooks** → **Add webhook**.
2. Fill in the details:
   - **Payload URL:**  
     `http://34.72.5.170:8080/github-webhook/`  
     *(Replace with your Jenkins URL)*
   - **Content type:** `application/json`
   - **Secret:** *(Not necessary, leave blank)*
   - **Enable SSL verification:** Enable if using HTTPS
3. Under **Which events would you like to trigger this webhook?**  
   - Tick **Just the push event**  
     (This means the pipeline triggers on every push)
4. Click **Add webhook**.

---

### Step 2: Configure Jenkins to Receive Webhook

1. Open **Jenkins** → Go to your **Pipeline** job → Click **Configure**.
2. Scroll down to **Build Triggers**.
3. Tick **GitHub hook trigger for GITScm polling**.
4. Click **Apply** and **Save**.
5. Your webhook trigger is now configured.

---

### Step 3: Test the Webhook Trigger

1. Open **VS Code**.
2. Make a slight change in the `Jenkinsfile` (e.g., add or modify an `echo` statement for demonstration).
3. Commit and **push** the code to GitHub.
4. Go to Jenkins Dashboard.
5. You should see your Jenkins pipeline **automatically triggered** and start running.

---

### Final Outcome

- Jenkins will automatically trigger ArgoCD sync as part of the pipeline.
- This completes the full GitOps pipeline successfully and automatically!

---

# 11. Restore from Machine Image (After Instance Deletion)

If you created a machine image from your GCP instance and then deleted the original instance, follow these steps to restore everything:

---

## 📸 Step 1: Create New VM Instance from Machine Image

1. Go to **GCP Console → Compute Engine → VM Instances**
2. Click **"Create Instance"**
3. Configure the instance:
   - **Name**: `gitops` (or your preferred name)
   - **Machine Type**:
     - Series: `E2`
     - Preset: `Standard`
     - Memory: `16 GB RAM`
   - **Boot Disk**: 
     - Click **"Change"**
     - Select **"Images"** tab
     - Choose your **machine image** from the list
     - Change size to `256 GB` if needed
   - **Networking**:
     - Enable HTTP and HTTPS traffic
4. Click **"Create"**

---

## 🔌 Step 2: Connect to the New VM Instance

- Use the **SSH** option provided in GCP to connect to the VM from the browser
- Or use SSH from your local machine:
  ```bash
  gcloud compute ssh gitops --zone=YOUR_ZONE
  ```

---

## 🐳 Step 3: Verify and Start Docker

Check if Docker is installed and start it:

```bash
# Check Docker status
systemctl status docker

# If Docker is not running, start it
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker is working
docker ps
docker run hello-world
```

---

## 🚀 Step 4: Start Minikube

Since Minikube was stopped when the instance was deleted, you need to restart it:

```bash
# Check Minikube status
minikube status

# Start Minikube cluster
minikube start

# Wait for Minikube to be ready (this may take a few minutes)
minikube status

# Verify Kubernetes cluster
kubectl get nodes
kubectl cluster-info
```

**Note**: If Minikube fails to start, you may need to delete the old cluster and create a new one:

```bash
# Delete old Minikube cluster
minikube delete

# Start fresh Minikube cluster
minikube start
```

---

## 🔄 Step 5: Restart Jenkins Container

Check if Jenkins container exists and restart it:

```bash
# Check if Jenkins container exists
docker ps -a | grep jenkins

# If Jenkins container exists but is stopped, start it
docker start jenkins

# If Jenkins container doesn't exist, create it again
docker run -d --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(which docker):/usr/bin/docker \
  -u root \
  -e DOCKER_GID=$(getent group docker | cut -d: -f3) \
  --network minikube \
  jenkins/jenkins:lts

# Verify Jenkins is running
docker ps
docker logs jenkins
```

**Important**: If you created a new Jenkins container, you'll need to:
- Get the new admin password: `docker logs jenkins`
- Reconfigure Jenkins (plugins, credentials, pipelines)
- Re-add all credentials (GitHub token, DockerHub token, kubeconfig)

---

## 🔧 Step 6: Update Jenkins Network (if needed)

If Jenkins was recreated, ensure it's on the Minikube network:

```bash
# Check Minikube network
docker network ls | grep minikube

# If Jenkins is not on minikube network, connect it
docker network connect minikube jenkins

# Verify
docker inspect jenkins | grep NetworkMode
```

---

## 📦 Step 7: Restore ArgoCD

ArgoCD should be restored from the machine image, but verify and restart if needed:

```bash
# Check ArgoCD namespace
kubectl get namespace | grep argocd

# If namespace doesn't exist, create it
kubectl create ns argocd

# Check ArgoCD pods
kubectl get pods -n argocd

# If pods are not running, reinstall ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for all pods to be ready
kubectl get pods -n argocd -w
```

**Wait until all ArgoCD pods are in "Running" state before proceeding.**

---

## 🔌 Step 8: Reconfigure ArgoCD Service

Check and update ArgoCD service to NodePort:

```bash
# Check current service type
kubectl get svc -n argocd

# If argocd-server is ClusterIP, change to NodePort
kubectl edit svc argocd-server -n argocd
# Change: type: ClusterIP → type: NodePort
# Save and exit (Ctrl+X, Y, Enter)

# Get the new NodePort
kubectl get svc -n argocd
# Note the NodePort number (e.g., 31704)
```

---

## 🔐 Step 9: Get ArgoCD Admin Password

```bash
# Get the admin password
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Note**: If the secret doesn't exist, ArgoCD will create it automatically on first install.

---

## 🌐 Step 10: Update Firewall Rules

Since you have a new VM instance with a new external IP, update firewall rules:

1. Go to **GCP Console → VPC Network → Firewall**
2. Check if the `allow-jenkins` rule exists
3. If not, create it:
   - Name: `allow-jenkins`
   - Direction: `ingress`
   - Action: `allow`
   - Targets: `All instances`
   - Source IP ranges: `0.0.0.0/0`
   - Allowed protocols and ports: `all`

---

## 🔄 Step 11: Update IP Addresses in Configuration

Since the VM has a new external IP, update the following:

### A. Update GitHub Webhook

1. Go to **GitHub Repository → Settings → Webhooks**
2. Edit the existing webhook
3. Update **Payload URL** to: `http://<NEW_VM_EXTERNAL_IP>:8080/github-webhook/`
4. Save

### B. Update ArgoCD Login in Jenkinsfile (if hardcoded)

If your Jenkinsfile has a hardcoded ArgoCD IP, update it:

```bash
# Get new VM external IP
curl ifconfig.me
# Or check in GCP Console

# Get ArgoCD NodePort
kubectl get svc -n argocd argocd-server

# Update Jenkinsfile with new IP:PORT
```

### C. Update kubeconfig (if needed)

If you need to regenerate kubeconfig:

```bash
# Get cluster info
kubectl cluster-info

# The cluster URL might have changed, update in Jenkins credentials if needed
```

---

## 🚀 Step 12: Restart Services and Verify

### Start Minikube Tunnel (in a separate terminal)

**Option 1: Run in background with nohup (Simple)**

```bash
# Start Minikube tunnel in background
nohup minikube tunnel > /tmp/minikube-tunnel.log 2>&1 &

# Check if it's running
ps aux | grep "minikube tunnel"

# View logs
tail -f /tmp/minikube-tunnel.log

# To stop it later
pkill -f "minikube tunnel"
```

**Option 2: Run in screen session (Recommended)**

```bash
# Install screen if not available
sudo apt-get install screen -y

# Start a screen session
screen -S minikube-tunnel

# Inside screen, run:
minikube tunnel

# Detach from screen: Press Ctrl+A, then D
# Reattach later: screen -r minikube-tunnel
# Kill screen session: screen -X -S minikube-tunnel quit
```

**Option 3: Run as systemd service (Persistent)**

```bash
# Create systemd service file
sudo vi /etc/systemd/system/minikube-tunnel.service
```

Add this content:
```ini
[Unit]
Description=Minikube Tunnel
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/minikube tunnel
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Replace YOUR_USERNAME with your actual username
sudo systemctl daemon-reload
sudo systemctl enable minikube-tunnel.service
sudo systemctl start minikube-tunnel.service

# Check status
sudo systemctl status minikube-tunnel.service

# View logs
sudo journalctl -u minikube-tunnel.service -f
```

### Port Forward ArgoCD (in another terminal)

**Option 1: Run in background with nohup**

```bash
# Get the NodePort first
NODEPORT=$(kubectl get svc -n argocd argocd-server -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')

# Port forward in background
nohup kubectl port-forward --address 0.0.0.0 service/argocd-server ${NODEPORT}:80 -n argocd > /tmp/argocd-portforward.log 2>&1 &

# Check if it's running
ps aux | grep "port-forward.*argocd-server"

# View logs
tail -f /tmp/argocd-portforward.log

# To stop it later
pkill -f "port-forward.*argocd-server"
```

**Option 2: Run in screen session**

```bash
# Start a screen session for ArgoCD port forwarding
screen -S argocd-portforward

# Get NodePort
NODEPORT=$(kubectl get svc -n argocd argocd-server -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')

# Run port forward
kubectl port-forward --address 0.0.0.0 service/argocd-server ${NODEPORT}:80 -n argocd

# Detach: Ctrl+A, then D
# Reattach: screen -r argocd-portforward
```

**Option 3: Run as systemd service**

```bash
# Create systemd service file
sudo vi /etc/systemd/system/argocd-portforward.service
```

Add this content (replace NODEPORT with actual value):
```ini
[Unit]
Description=ArgoCD Port Forward
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/kubectl port-forward --address 0.0.0.0 service/argocd-server 32166:80 -n argocd
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable argocd-portforward.service
sudo systemctl start argocd-portforward.service
sudo systemctl status argocd-portforward.service
```

### Port Forward Application (if needed)

**Option 1: Run in background with nohup**

```bash
# Port forward application in background
nohup kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80 > /tmp/app-portforward.log 2>&1 &

# Check if it's running
s

# View logs
tail -f /tmp/app-portforward.log

# To stop it later
pkill -f "port-forward.*llmops-service"
```

**Option 2: Run in screen session**

```bash
# Start a screen session for app port forwarding
screen -S app-portforward

# Run port forward
kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80

# Detach: Ctrl+A, then D
# Reattach: screen -r app-portforward
```

**Option 3: Run as systemd service**

```bash
# Create systemd service file
sudo vi /etc/systemd/system/app-portforward.service
```

Add this content:
```ini
[Unit]
Description=Application Port Forward
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/usr/local/bin/kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable app-portforward.service
sudo systemctl start app-portforward.service
sudo systemctl status app-portforward.service
```

## 🔄 Setting Up Persistent Port Forwarding with systemd

To make port forwarding persistent and start automatically on boot, set up systemd services:

### Prerequisites

```bash
# Get your username
whoami

# Get your home directory
echo $HOME

# Get kubectl path
which kubectl

# Get minikube path
which minikube

# Get KUBECONFIG path (usually ~/.kube/config)
echo $KUBECONFIG || echo ~/.kube/config
```

### Step 1: Create Minikube Tunnel Service

```bash
# Create the service file
sudo vi /etc/systemd/system/minikube-tunnel.service
```

Add this content (replace `YOUR_USERNAME` with your actual username):

```ini
[Unit]
Description=Minikube Tunnel
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
Environment="HOME=/home/YOUR_USERNAME"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/local/bin/minikube tunnel
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `YOUR_USERNAME` with your actual username (from `whoami` command).

### Step 2: Create ArgoCD Port Forward Service

```bash
# First, get the NodePort (replace with your actual NodePort)
kubectl get svc -n argocd argocd-server -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}'

# Create the service file
sudo vi /etc/systemd/system/argocd-portforward.service
```

Add this content (replace `YOUR_USERNAME` and `NODEPORT`):

```ini
[Unit]
Description=ArgoCD Port Forward
After=network.target minikube-tunnel.service
Wants=minikube-tunnel.service
Requires=minikube-tunnel.service

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
Environment="HOME=/home/YOUR_USERNAME"
Environment="KUBECONFIG=/home/YOUR_USERNAME/.kube/config"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/local/bin/kubectl port-forward --address 0.0.0.0 service/argocd-server NODEPORT:80 -n argocd
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Important:** 
- Replace `YOUR_USERNAME` with your actual username
- Replace `NODEPORT` with the actual NodePort from the command above (e.g., `32166`)

### Step 3: Create Application Port Forward Service

```bash
# Create the service file
sudo vi /etc/systemd/system/app-portforward.service
```

Add this content (replace `YOUR_USERNAME`):

```ini
[Unit]
Description=Application Port Forward
After=network.target minikube-tunnel.service
Wants=minikube-tunnel.service
Requires=minikube-tunnel.service

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
Environment="HOME=/home/YOUR_USERNAME"
Environment="KUBECONFIG=/home/YOUR_USERNAME/.kube/config"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/usr/local/bin/kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `YOUR_USERNAME` with your actual username.

### Step 4: Enable and Start Services

```bash
# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable minikube-tunnel.service
sudo systemctl enable argocd-portforward.service
sudo systemctl enable app-portforward.service

# Start services
sudo systemctl start minikube-tunnel.service
sudo systemctl start argocd-portforward.service
sudo systemctl start app-portforward.service

# Check status of all services
sudo systemctl status minikube-tunnel.service
sudo systemctl status argocd-portforward.service
sudo systemctl status app-portforward.service
```

### Step 5: Verify Services Are Running

```bash
# Check all services status
sudo systemctl list-units | grep -E "(tunnel|portforward)"

# Check if processes are running
ps aux | grep -E "(minikube tunnel|port-forward)" | grep -v grep

# View logs
sudo journalctl -u minikube-tunnel.service -f
sudo journalctl -u argocd-portforward.service -f
sudo journalctl -u app-portforward.service -f
```

### Step 6: Test Access

- **ArgoCD**: `http://<VM_EXTERNAL_IP>:<NODEPORT>`
- **Application**: `http://<VM_EXTERNAL_IP>:9090`

### Managing Services

**Stop a service:**
```bash
sudo systemctl stop minikube-tunnel.service
sudo systemctl stop argocd-portforward.service
sudo systemctl stop app-portforward.service
```

**Start a service:**
```bash
sudo systemctl start minikube-tunnel.service
sudo systemctl start argocd-portforward.service
sudo systemctl start app-portforward.service
```

**Restart a service:**
```bash
sudo systemctl restart minikube-tunnel.service
sudo systemctl restart argocd-portforward.service
sudo systemctl restart app-portforward.service
```

**Disable auto-start on boot:**
```bash
sudo systemctl disable minikube-tunnel.service
sudo systemctl disable argocd-portforward.service
sudo systemctl disable app-portforward.service
```

**View service logs:**
```bash
# View recent logs
sudo journalctl -u minikube-tunnel.service -n 50

# Follow logs in real-time
sudo journalctl -u argocd-portforward.service -f

# View logs since boot
sudo journalctl -u app-portforward.service -b
```

### Troubleshooting

**If services fail to start:**

1. **Check service status:**
   ```bash
   sudo systemctl status minikube-tunnel.service
   ```

2. **Check logs for errors:**
   ```bash
   sudo journalctl -u minikube-tunnel.service -n 100
   ```

3. **Verify paths are correct:**
   ```bash
   which minikube
   which kubectl
   ```

4. **Check if minikube is running:**
   ```bash
   minikube status
   ```

5. **Verify KUBECONFIG:**
   ```bash
   kubectl get nodes
   ```

**If port forwarding fails:**

- Ensure minikube tunnel is running first
- Check if the NodePort is correct: `kubectl get svc -n argocd argocd-server`
- Verify services exist: `kubectl get svc -n argocd`

**If services don't start on boot:**

- Check if services are enabled: `sudo systemctl is-enabled minikube-tunnel.service`
- Verify systemd dependencies: `systemctl list-dependencies minikube-tunnel.service`

### Quick Reference: Managing Background Processes

**Check all port forwarding processes:**
```bash
ps aux | grep port-forward
ps aux | grep "minikube tunnel"
```

**Stop all port forwarding:**
```bash
pkill -f "port-forward"
pkill -f "minikube tunnel"
```

**List all screen sessions:**
```bash
screen -ls
```

**Kill a specific screen session:**
```bash
screen -X -S session-name quit
```

**Check systemd services:**
```bash
sudo systemctl list-units | grep -E "(tunnel|portforward)"
```

---

## ✅ Step 13: Verify Everything is Working

### Verify Docker
```bash
docker ps
```

### Verify Minikube
```bash
minikube status
kubectl get nodes
```

### Verify Jenkins
- Access: `http://<NEW_VM_EXTERNAL_IP>:8080`
- Login with admin credentials
- Check if pipelines are configured

### Verify ArgoCD
- Access: `http://<NEW_VM_EXTERNAL_IP>:<NODEPORT>`
- Login with admin and password from Step 9
- Check if applications are synced

### Verify Application
- Access: `http://<NEW_VM_EXTERNAL_IP>:9090`
- Should see Study Buddy AI application

**If application is not accessible, troubleshoot:**

#### Step 1: Check if port-forward is running
```bash
# Check if port-forward process is running
ps aux | grep "port-forward.*llmops-service"

# If not running, start it:
nohup kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80 > /tmp/app-portforward.log 2>&1 &
```

#### Step 2: Check if application pods are running
```bash
# Check pods in argocd namespace
kubectl get pods -n argocd | grep llmops-app

# Check pod status and events
kubectl describe pod <pod-name> -n argocd

# Check pod logs
kubectl logs <pod-name> -n argocd
```

#### Step 3: Check if service exists
```bash
# Check service
kubectl get svc -n argocd | grep llmops-service

# Get service details
kubectl get svc llmops-service -n argocd -o yaml
```

#### Step 4: Check if deployment exists and is ready
```bash
# Check deployment
kubectl get deployment -n argocd | grep llmops-app

# Check deployment details
kubectl describe deployment llmops-app -n argocd

# Check replicasets
kubectl get rs -n argocd | grep llmops-app
```

#### Step 5: Verify ArgoCD application status
```bash
# List ArgoCD applications
kubectl get applications -n argocd

# Check application sync status
argocd app get <app-name>

# If out of sync, sync it
argocd app sync <app-name>
```

#### Step 6: Check if minikube tunnel is running
```bash
# Check if minikube tunnel is running
ps aux | grep "minikube tunnel"

# If not running, start it:
nohup minikube tunnel > /tmp/minikube-tunnel.log 2>&1 &
```

#### Step 7: Alternative - Use NodePort directly
```bash
# Get the NodePort for the service
kubectl get svc llmops-service -n argocd

# Access via NodePort (if service has NodePort type)
# http://<VM_EXTERNAL_IP>:<NODEPORT>
```

#### Step 8: Check firewall rules
```bash
# Ensure firewall allows traffic on port 9090
# In GCP Console: VPC Network → Firewall Rules
# Should have a rule allowing ingress on port 9090
```

#### Common Issues and Fixes:

**Issue: Pods in ImagePullBackOff**
```bash
# Check if image exists and is accessible
docker pull blessedman776/studybuddy:<tag>

# Update deployment with correct image tag
kubectl set image deployment/llmops-app llmops-app=blessedman776/studybuddy:<tag> -n argocd
```

**Issue: Pods in CrashLoopBackOff**
```bash
# Check pod logs for errors
kubectl logs <pod-name> -n argocd --previous

# Check if GROQ_API_KEY secret exists
kubectl get secret groq-api-secret -n argocd

# If missing, create it:
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="your-groq-api-key" \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  -n argocd

# If secret already exists, update it:
# Get existing GROQ_API_KEY
GROQ_KEY=$(kubectl get secret groq-api-secret -n argocd -o jsonpath='{.data.GROQ_API_KEY}' | base64 -d)
# Delete and recreate with both keys
kubectl delete secret groq-api-secret -n argocd
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="$GROQ_KEY" \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  -n argocd
```

**Issue: Port-forward dies immediately**
```bash
# Check if service selector matches pod labels
kubectl get svc llmops-service -n argocd -o yaml | grep selector
kubectl get pods -n argocd --show-labels | grep llmops-app

# Ensure labels match
```

**Issue: Application Not Loading on Port 9090 - Complete Troubleshooting Guide**

Follow these steps in order:

#### Step 1: Check if Port Forward Service is Running

```bash
# Check systemd service status
sudo systemctl status app-portforward.service

# Check if process is running
ps aux | grep "port-forward.*llmops-service" | grep -v grep

# Check service logs
sudo journalctl -u app-portforward.service -n 50 --no-pager
```

**If service is not running:**
```bash
# Start the service
sudo systemctl start app-portforward.service

# Check status again
sudo systemctl status app-portforward.service
```

#### Step 2: Check if Application Pods are Running

```bash
# Check if pods exist and are running
kubectl get pods -n argocd | grep llmops-app

# Check pod status in detail
kubectl get pods -n argocd -l app=llmops-app -o wide

# Check pod logs for errors
kubectl logs -n argocd -l app=llmops-app --tail=50
```

**If pods are not running:**
```bash
# Check pod events
kubectl describe pod <pod-name> -n argocd

# Check if pods are in CrashLoopBackOff
kubectl get pods -n argocd | grep llmops-app
```

#### Step 3: Check if Service Exists

```bash
# Check if service exists
kubectl get svc -n argocd | grep llmops-service

# Get service details
kubectl get svc llmops-service -n argocd -o yaml

# Check service endpoints
kubectl get endpoints llmops-service -n argocd
```

**If service doesn't exist:**
```bash
# Apply the service manifest
kubectl apply -f manifests/service.yaml

# Verify service was created
kubectl get svc -n argocd
```

#### Step 4: Verify Service Selector Matches Pod Labels

```bash
# Check service selector
kubectl get svc llmops-service -n argocd -o jsonpath='{.spec.selector}'

# Check pod labels
kubectl get pods -n argocd -l app=llmops-app --show-labels

# They should match! Service selector should match pod labels
```

**If they don't match, fix the service:**
```bash
# Edit the service
kubectl edit svc llmops-service -n argocd

# Or reapply the service manifest
kubectl apply -f manifests/service.yaml
```

#### Step 5: Check if Minikube Tunnel is Running

```bash
# Check minikube tunnel service
sudo systemctl status minikube-tunnel.service

# Check if process is running
ps aux | grep "minikube tunnel" | grep -v grep

# If not running, start it
sudo systemctl start minikube-tunnel.service
```

#### Step 6: Test Port Forwarding Manually

```bash
# Stop the systemd service temporarily
sudo systemctl stop app-portforward.service

# Try port forwarding manually to see errors
kubectl port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80

# If it works manually, the issue is with the systemd service
# If it doesn't work, check the error message
```

#### Step 7: Check if Port 9090 is Listening

```bash
# Check if port 9090 is listening
sudo netstat -tlnp | grep 9090
# OR
sudo ss -tlnp | grep 9090

# Check from localhost
curl http://localhost:9090

# Check from external IP (replace with your VM IP)
curl http://<VM_EXTERNAL_IP>:9090
```

#### Step 8: Check Firewall Rules

**For GCP (Google Cloud Platform):**

Create a firewall rule to allow external access to port 9090:

**Method 1: Via GCP Console (Recommended)**

1. **Open GCP Console:**
   - Go to: https://console.cloud.google.com/
   - Make sure you're in the correct project

2. **Navigate to Firewall Rules:**
   - Click on **"☰" (Hamburger menu)** in the top left
   - Go to **"VPC Network"** → **"Firewall"**
   - Or direct link: https://console.cloud.google.com/networking/firewalls

3. **Create New Firewall Rule:**
   - Click **"CREATE FIREWALL RULE"** button at the top

4. **Fill in the Firewall Rule Details:**
   - **Name:** `allow-port-9090`
   - **Description:** `Allow ingress traffic on port 9090 for Study Buddy AI application`
   - **Network:** Select `default` (or your VPC network name)
   - **Priority:** `1000` (default is fine)
   - **Direction of traffic:** Select **"Ingress"**
   - **Action on match:** Select **"Allow"**

5. **Configure Targets:**
   - **Targets:** Select **"All instances in the network"**
   - (Or select specific target tags if you want to limit to specific VMs)

6. **Configure Source:**
   - **Source IP ranges:** Enter `0.0.0.0/0` (allows from anywhere)
   - (Or restrict to specific IP ranges for security)

7. **Configure Protocols and Ports:**
   - Select **"Specified protocols and ports"**
   - Check **"tcp"**
   - In the text box, enter: `9090`

8. **Create the Rule:**
   - Click **"CREATE"** button at the bottom
   - Wait 1-2 minutes for the rule to propagate

9. **Verify the Rule:**
   - You should see `allow-port-9090` in the firewall rules list
   - Status should be **"Enabled"**

**Method 2: Via gcloud CLI (if authenticated)**

```bash
# Authenticate first
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create firewall rule
gcloud compute firewall-rules create allow-port-9090 \
  --allow tcp:9090 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow port 9090 for Study Buddy AI" \
  --network default \
  --direction INGRESS \
  --priority 1000
```

**Method 3: Check Local Firewall (if ufw is enabled)**

```bash
# Check local firewall status
sudo ufw status

# If ufw is active, allow port 9090
sudo ufw allow 9090/tcp

# Verify
sudo ufw status | grep 9090
```

**After creating the firewall rule:**

1. Wait 1-2 minutes for the rule to propagate
2. Test external access:
   ```bash
   # Get your external IP
   curl ifconfig.me
   
   # Test from your local machine (not the VM)
   curl -I http://<YOUR_EXTERNAL_IP>:9090
   ```
3. Open in browser: `http://<YOUR_EXTERNAL_IP>:9090`

#### Step 9: Check Application Deployment

```bash
# Check deployment status
kubectl get deployment llmops-app -n argocd

# Check deployment details
kubectl describe deployment llmops-app -n argocd

# Check if deployment has correct image
kubectl get deployment llmops-app -n argocd -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check replicasets
kubectl get rs -n argocd | grep llmops-app
```

#### Step 10: Check Application Container Logs

```bash
# Get pod name
POD_NAME=$(kubectl get pods -n argocd -l app=llmops-app -o jsonpath='{.items[0].metadata.name}')

# Check logs
kubectl logs $POD_NAME -n argocd

# Check previous logs if container restarted
kubectl logs $POD_NAME -n argocd --previous

# Check if Streamlit is running on port 8501 inside container
kubectl exec -it $POD_NAME -n argocd -- netstat -tlnp | grep 8501
```

#### Step 11: Verify Service Port Mapping

```bash
# Check service port configuration
kubectl get svc llmops-service -n argocd -o yaml | grep -A 5 ports

# Should show:
# - port: 80
#   targetPort: 8501
```

**If targetPort is wrong:**
```bash
# Edit the service
kubectl edit svc llmops-service -n argocd
# Change targetPort to 8501 (Streamlit default port)
```

#### Step 12: Quick Fix - Restart Everything

```bash
# Restart all services
sudo systemctl restart minikube-tunnel.service
sleep 5
sudo systemctl restart argocd-portforward.service
sudo systemctl restart app-portforward.service

# Check status
sudo systemctl status app-portforward.service
```

#### Step 13: Alternative - Use NodePort Instead

If port-forwarding continues to fail, you can expose the service as NodePort:

```bash
# Edit the service to use NodePort
kubectl edit svc llmops-service -n argocd

# Change: type: NodePort
# Save and exit

# Get the NodePort
kubectl get svc llmops-service -n argocd

# Access via: http://<VM_EXTERNAL_IP>:<NODEPORT>
```

#### Common Issues and Solutions

**Issue 1: Service selector doesn't match pod labels**
```bash
# Fix: Update service selector or pod labels to match
kubectl get svc llmops-service -n argocd -o yaml | grep selector
kubectl get pods -n argocd -l app=llmops-app --show-labels
```

**Issue 2: Pods are in ImagePullBackOff**
```bash
# Check image name
kubectl get deployment llmops-app -n argocd -o jsonpath='{.spec.template.spec.containers[0].image}'

# Update deployment with correct image
kubectl set image deployment/llmops-app llmops-app=blessedman776/studybuddy:<tag> -n argocd
```

**Issue 3: Pods are in CrashLoopBackOff**
```bash
# Check logs
kubectl logs <pod-name> -n argocd --previous

# Check if GROQ_API_KEY secret exists
kubectl get secret groq-api-secret -n argocd

# If missing, create it:
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="your-groq-api-key" \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  -n argocd

# If secret already exists, update it:
# Get existing GROQ_API_KEY
GROQ_KEY=$(kubectl get secret groq-api-secret -n argocd -o jsonpath='{.data.GROQ_API_KEY}' | base64 -d)
# Delete and recreate with both keys
kubectl delete secret groq-api-secret -n argocd
kubectl create secret generic groq-api-secret \
  --from-literal=GROQ_API_KEY="$GROQ_KEY" \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  -n argocd
```

**Issue 4: Port 9090 is already in use**
```bash
# Find what's using port 9090
sudo lsof -i :9090
# OR
sudo netstat -tlnp | grep 9090

# Kill the process or use a different port
```

**Issue: Cannot connect to port 9090**
```bash
# Test from VM itself
curl http://localhost:9090

# Check if port is listening
netstat -tlnp | grep 9090
# OR
ss -tlnp | grep 9090

# Check firewall
sudo ufw status
# OR check GCP firewall rules
```

---

## 🔄 Step 14: Re-sync ArgoCD Applications

If ArgoCD applications are out of sync:

```bash
# List applications
kubectl get applications -n argocd

# Sync manually (replace 'gitops' with your app name)
argocd app sync gitops

# Or use ArgoCD UI to sync
```

---

## 📝 Step 15: Reconfigure Jenkins (if container was recreated)

If you had to recreate the Jenkins container, you'll need to:

1. **Re-add Credentials**:
   - GitHub Personal Access Token
   - DockerHub Access Token
   - kubeconfig file

2. **Reconfigure Pipeline**:
   - Create pipeline job again
   - Configure SCM settings
   - Update any hardcoded IPs

3. **Reinstall Plugins** (if needed):
   - Docker
   - Docker Pipeline
   - Kubernetes

---

## 🎯 Quick Restart Checklist

Use this checklist to quickly verify everything is restored:

- [ ] New VM instance created from machine image
- [ ] Docker is running (`systemctl status docker`)
- [ ] Minikube is started (`minikube status`)
- [ ] Jenkins container is running (`docker ps | grep jenkins`)
- [ ] ArgoCD pods are running (`kubectl get pods -n argocd`)
- [ ] ArgoCD service is NodePort (`kubectl get svc -n argocd`)
- [ ] Firewall rules are configured
- [ ] GitHub webhook updated with new IP
- [ ] Jenkins credentials re-added (if needed)
- [ ] ArgoCD applications synced
- [ ] Application accessible via browser

---

## 🆘 Troubleshooting

### Minikube won't start
```bash
minikube delete
minikube start --driver=docker
```

### Jenkins can't access Docker
```bash
# Ensure Jenkins is on minikube network
docker network connect minikube jenkins

# Restart Jenkins
docker restart jenkins
```

### ArgoCD pods stuck in Pending
```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name> -n argocd
```

### ArgoCD pods in ImagePullBackOff status

This error means Kubernetes cannot pull container images. Here's how to fix it:

#### Step 1: Diagnose the issue
```bash
# Check detailed pod status
kubectl describe pod argocd-server-57d9cc9bcf-q8cnd -n argocd

# Check events for all pods
kubectl get events -n argocd --sort-by='.lastTimestamp'
```

#### Step 2: Check network connectivity

**First, test connectivity from the VM itself:**

```bash
# Test if you can reach container registries from VM
curl -I https://quay.io
curl -I https://docker.io
ping -c 3 8.8.8.8  # Test basic internet connectivity

# Test DNS resolution
nslookup quay.io
nslookup docker.io
```

**Then test from inside Minikube:**

```bash
# Test DNS from Minikube
minikube ssh -- nslookup quay.io
minikube ssh -- nslookup docker.io

# Test internet connectivity from Minikube
minikube ssh -- ping -c 3 8.8.8.8

# Try to pull an image manually from Minikube
minikube ssh -- docker pull quay.io/argoproj/argocd:v2.8.4
```

**If DNS or connectivity fails, fix DNS configuration:**

**Method 1: Configure CoreDNS in Kubernetes (Recommended)**

```bash
# Get the CoreDNS configmap
kubectl get configmap coredns -n kube-system -o yaml > coredns-config.yaml

# Edit the configmap to add Google DNS as forward
kubectl edit configmap coredns -n kube-system

# In the editor, find the "forward" section and change it to:
# forward . 8.8.8.8 8.8.4.4
# Or add it if it doesn't exist

# Restart CoreDNS pods
kubectl delete pods -n kube-system -l k8s-app=kube-dns

# Wait for CoreDNS to restart
kubectl get pods -n kube-system -w

# Test DNS from Minikube
minikube ssh -- nslookup quay.io
```

**Method 2: Configure DNS in Minikube's Docker container**

```bash
# SSH into Minikube
minikube ssh

# Edit DNS configuration
sudo vi /etc/resolv.conf

# Add or replace with:
# nameserver 8.8.8.8
# nameserver 8.8.4.4

# Save and exit, then restart Docker
sudo systemctl restart docker

# Exit Minikube
exit

# Test DNS
minikube ssh -- nslookup quay.io
```

**Method 3: Delete and recreate Minikube (if above methods don't work)**

```bash
# Delete Minikube
minikube delete

# Start fresh Minikube
minikube start

# Then configure CoreDNS using Method 1 above
```

**Method 4: Use host's DNS resolver**

```bash
# Get host's DNS server
cat /etc/resolv.conf

# Configure CoreDNS to forward to host DNS (see Method 1)
```

#### Step 3: Reinstall ArgoCD (Recommended Solution)

The easiest fix is to reinstall ArgoCD, which will pull fresh images:

```bash
# Delete existing ArgoCD installation
kubectl delete namespace argocd

# Wait a moment for cleanup
sleep 10

# Reinstall ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to start (this may take 2-5 minutes)
kubectl get pods -n argocd -w

# Check pod status
kubectl get pods -n argocd
```

#### Step 4: If reinstall doesn't work, try pulling images manually

```bash
# Enter Minikube's Docker environment
minikube ssh

# Inside Minikube, pull ArgoCD images manually
docker pull quay.io/argoproj/argocd:v2.8.4
docker pull quay.io/argoproj/argocd-repo-server:v2.8.4
docker pull quay.io/argoproj/argocd-dex:v2.8.4
docker pull quay.io/argoproj/argocd-applicationset:v0.4.1
docker pull redis:7-alpine
docker pull quay.io/argoproj/argocd-notifications:v1.8.0

# Exit Minikube
exit

# Delete pods to force recreation
kubectl delete pods --all -n argocd

# Watch pods restart
kubectl get pods -n argocd -w
```

#### Step 5: Alternative - Use Minikube's image cache

```bash
# Load images into Minikube's cache
minikube image load quay.io/argoproj/argocd:v2.8.4

# Or configure Minikube to use local Docker registry
eval $(minikube docker-env)
```

#### Step 6: Check DNS resolution and GCP network settings

**If DNS or connectivity fails, check GCP network configuration:**

```bash
# Test DNS inside Minikube
minikube ssh -- nslookup quay.io

# If DNS fails, configure CoreDNS (see Method 1 in Step 2 above)
# Or configure DNS in Minikube's Docker container (see Method 2 in Step 2 above)
```

**Check GCP Firewall Rules for outbound traffic:**

1. Go to **GCP Console → VPC Network → Firewall Rules**
2. Ensure there's a rule allowing **egress (outbound)** traffic:
   - Direction: `Egress`
   - Action: `Allow`
   - Targets: `All instances in the network`
   - Destination IP ranges: `0.0.0.0/0`
   - Protocols and ports: `All` or `tcp:443, tcp:80, tcp:53, udp:53`

**If no egress rule exists, create one:**

```bash
# Using gcloud CLI (if available)
gcloud compute firewall-rules create allow-egress \
  --direction=EGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=all \
  --destination-ranges=0.0.0.0/0
```

**Or create via GCP Console:**
- Go to **VPC Network → Firewall → Create Firewall Rule**
- Name: `allow-egress`
- Direction: `Egress`
- Action: `Allow`
- Targets: `All instances in the network`
- Destination IP ranges: `0.0.0.0/0`
- Protocols and ports: `All`

**Check VM's external IP and network tags:**

```bash
# Check if VM has external IP
curl ifconfig.me

# Check network interface
ip addr show

# Test if VM can reach external services
curl -v https://quay.io
```

#### Step 7: Verify ArgoCD is working

```bash
# Check all pods are running
kubectl get pods -n argocd

# All pods should show "Running" status
# If any are still ImagePullBackOff, check the specific pod:
kubectl describe pod <pod-name> -n argocd

# Get ArgoCD admin password
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### Application pods in ImagePullBackOff

If your application pods (llmops-app) are also in ImagePullBackOff:

```bash
# Check what image it's trying to pull
kubectl describe pod llmops-app-7dc9494c78-cvpgv -n argocd

# Verify the image exists in DockerHub
# If using a private registry, ensure image pull secrets are configured

# Delete the failing pods (they will be recreated)
kubectl delete pod llmops-app-7dc9494c78-cvpgv -n argocd

# Or delete all app pods
kubectl delete pods -l app=llmops-app -n argocd
```

### Can't access services externally
- Verify firewall rules allow traffic
- Check if services are NodePort type
- Ensure port-forwarding is running
- Verify external IP is correct

---

https://github.com/data-guru0/STUDY-BUDDY-AI