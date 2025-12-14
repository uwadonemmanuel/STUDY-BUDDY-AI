#!/bin/bash

# Setup Persistent Port Forwarding with systemd
# This script creates systemd services for minikube tunnel and port forwarding

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up persistent port forwarding services...${NC}"

# Get current user
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
KUBECTL_PATH=$(which kubectl)
MINIKUBE_PATH=$(which minikube)
KUBECONFIG_PATH="${HOME_DIR}/.kube/config"

echo -e "${YELLOW}Detected settings:${NC}"
echo "  Username: $CURRENT_USER"
echo "  Home: $HOME_DIR"
echo "  kubectl: $KUBECTL_PATH"
echo "  minikube: $MINIKUBE_PATH"
echo "  kubeconfig: $KUBECONFIG_PATH"

# Verify kubectl and minikube
if [ ! -f "$KUBECTL_PATH" ]; then
    echo -e "${RED}Error: kubectl not found at $KUBECTL_PATH${NC}"
    exit 1
fi

if [ ! -f "$MINIKUBE_PATH" ]; then
    echo -e "${RED}Error: minikube not found at $MINIKUBE_PATH${NC}"
    exit 1
fi

# Get ArgoCD NodePort
echo -e "${YELLOW}Getting ArgoCD NodePort...${NC}"
NODEPORT=$(kubectl get svc -n argocd argocd-server -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}' 2>/dev/null || echo "32166")

if [ -z "$NODEPORT" ]; then
    echo -e "${YELLOW}Warning: Could not get NodePort, using default 32166${NC}"
    NODEPORT="32166"
fi

echo -e "${GREEN}ArgoCD NodePort: $NODEPORT${NC}"

# Create Minikube Tunnel Service
echo -e "${YELLOW}Creating minikube-tunnel.service...${NC}"
sudo tee /etc/systemd/system/minikube-tunnel.service > /dev/null <<EOF
[Unit]
Description=Minikube Tunnel
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
Environment="HOME=$HOME_DIR"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$MINIKUBE_PATH tunnel
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create ArgoCD Port Forward Service
echo -e "${YELLOW}Creating argocd-portforward.service...${NC}"
sudo tee /etc/systemd/system/argocd-portforward.service > /dev/null <<EOF
[Unit]
Description=ArgoCD Port Forward
After=network.target minikube-tunnel.service
Wants=minikube-tunnel.service
Requires=minikube-tunnel.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
Environment="HOME=$HOME_DIR"
Environment="KUBECONFIG=$KUBECONFIG_PATH"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$KUBECTL_PATH port-forward --address 0.0.0.0 service/argocd-server $NODEPORT:80 -n argocd
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create Application Port Forward Service
echo -e "${YELLOW}Creating app-portforward.service...${NC}"
sudo tee /etc/systemd/system/app-portforward.service > /dev/null <<EOF
[Unit]
Description=Application Port Forward
After=network.target minikube-tunnel.service
Wants=minikube-tunnel.service
Requires=minikube-tunnel.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
Environment="HOME=$HOME_DIR"
Environment="KUBECONFIG=$KUBECONFIG_PATH"
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$KUBECTL_PATH port-forward svc/llmops-service -n argocd --address 0.0.0.0 9090:80
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo -e "${YELLOW}Reloading systemd...${NC}"
sudo systemctl daemon-reload

# Enable services
echo -e "${YELLOW}Enabling services to start on boot...${NC}"
sudo systemctl enable minikube-tunnel.service
sudo systemctl enable argocd-portforward.service
sudo systemctl enable app-portforward.service

# Start services
echo -e "${YELLOW}Starting services...${NC}"
sudo systemctl start minikube-tunnel.service
sleep 5  # Wait for minikube tunnel to start
sudo systemctl start argocd-portforward.service
sudo systemctl start app-portforward.service

# Check status
echo -e "${GREEN}Checking service status...${NC}"
echo ""
echo "Minikube Tunnel:"
sudo systemctl status minikube-tunnel.service --no-pager -l | head -10

echo ""
echo "ArgoCD Port Forward:"
sudo systemctl status argocd-portforward.service --no-pager -l | head -10

echo ""
echo "Application Port Forward:"
sudo systemctl status app-portforward.service --no-pager -l | head -10

echo ""
echo -e "${GREEN}✅ Services setup complete!${NC}"
echo ""
echo "Services are now:"
echo "  - Enabled to start on boot"
echo "  - Configured to auto-restart on failure"
echo "  - Running in the background"
echo ""
echo "Useful commands:"
echo "  Check status: sudo systemctl status minikube-tunnel.service"
echo "  View logs:    sudo journalctl -u minikube-tunnel.service -f"
echo "  Restart:      sudo systemctl restart minikube-tunnel.service"
echo "  Stop:         sudo systemctl stop minikube-tunnel.service"

