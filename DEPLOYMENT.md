# Deploying School Management System on Google Cloud

This guide walks through deploying the School Management System on Google Cloud Platform using Ubuntu 20.04 LTS Minimal with an external IP address (no domain).

## 1. Create a VM Instance on Google Cloud

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project (or select existing one)
3. Navigate to Compute Engine → VM instances
4. Click "Create Instance"
5. Configure your instance:
   - Name: school-management-server
   - Region: (select one close to your users)
   - Machine type: e2-small (2 vCPU, 2 GB memory) should be sufficient
   - Boot disk: Ubuntu 20.04 LTS Minimal
   - Firewall: Allow HTTP and HTTPS traffic
6. Click "Create"

## 2. Connect to Your VM

Once the VM is running:
```bash
gcloud compute ssh school-management-server
```

Or use the SSH button in the Google Cloud Console.

## 3. Update and Install Dependencies

```bash
# Update packages
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y ca-certificates curl gnupg lsb-release git
```

## 4. Install Docker

```bash
# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index and install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Apply the new group (you may need to log out and back in again)
newgrp docker
```

## 5. Install Docker Compose

```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.16.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

## 6. Clone and Deploy Your Application

```bash
# Create a directory for your application
mkdir -p ~/school-management
cd ~/school-management

# Clone your application files (or transfer them using SCP/SFTP)
# For example:
git clone <your-repo-url> .

# Or upload your files using SCP from your local machine:
# (Run this on your local machine)
# scp -r /path/to/your/project/* your-username@external-ip:~/school-management/
```

## 7. Configure Your Application

```bash
# Create .env file
cp .env.example .env

# Edit the .env file with production settings
nano .env
```

Modify these settings in your .env file:
```
SECRET_KEY=a_secure_random_string_here
FLASK_ENV=production
```

## 8. Configure External Access

Edit the docker-compose.yml to ensure it binds to the correct ports:

```bash
nano docker-compose.yml
```

Make sure you have:
```yaml
services:
  web:
    # ... other settings ...
    ports:
      - "80:5002"  # Map port 80 (external) to 5002 (container)
```

## 9. Start the Application

```bash
# Build and start containers
docker-compose up -d --build

# Check if the containers are running
docker ps
```

## 10. Configure Firewall

The Google Cloud firewall should already allow HTTP (port 80) if you selected that option when creating the VM. If not:

```bash
# Allow HTTP traffic (port 80)
gcloud compute firewall-rules create allow-http --allow tcp:80 --target-tags=http-server --description="Allow HTTP traffic"

# Add the http-server tag to your VM if needed
gcloud compute instances add-tags school-management-server --tags=http-server
```

## 11. Testing Your Deployment

Your application should now be accessible at the external IP address of your VM:
```
http://<your-vm-external-ip>
```

You can find your VM's external IP in the Google Cloud Console or by running:
```bash
gcloud compute instances describe school-management-server --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

## 12. Maintenance and Monitoring

```bash
# View logs
docker-compose logs -f

# Restart the application
docker-compose restart

# Stop the application
docker-compose down

# Update the application (after pulling new code)
docker-compose up -d --build
```

## Security Notes

1. The setup above uses HTTP only. For production, consider setting up HTTPS with a certificate.
2. The database is stored in a Docker volume. For production systems with critical data, consider using a managed database service.
3. Set up regular backups of your data volume.

## Database Backups

To create a backup of your SQLite database:

```bash
# Find the volume location
docker volume inspect school_management_data

# Create a backup
sudo cp /var/lib/docker/volumes/school_management_data/_data/school_management.db ~/backups/school_management_$(date +%Y%m%d).db
```

## Troubleshooting

1. **Application not starting**: Check logs with `docker-compose logs`
2. **Cannot connect to the application**: Verify firewall settings and that the application is listening on the correct port
3. **Database errors**: Check permissions on the data volume
4. **VM resources**: If the application is slow, consider upgrading your VM to a larger instance type