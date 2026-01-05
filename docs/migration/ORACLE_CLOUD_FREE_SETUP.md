# Oracle Cloud Free Tier Setup - 100% MIỄN PHÍ VĨNH VIỄN

**Cost: $0/month FOREVER**

---

## 🎁 ALWAYS FREE TIER (Không bao giờ hết hạn)

```yaml
Compute:
  - 4x Ampere ARM Instances (3000 OCPU hours/month)
  - Total RAM: 24GB
  - Total CPU: 4 cores (Ampere A1)
  - Arch: ARM64 (aarch64)

Storage:
  - 200GB Block Volume (boot + data)

Network:
  - 10TB Outbound Transfer/month
  - 1 Public IPv4 (free)

Database (Optional):
  - 2x Autonomous DB instances (0.02 OCPU each)
  - 20GB storage

Load Balancer:
  - 1x flexible load balancer (10Mbps)
```

**Link đăng ký:** https://www.oracle.com/cloud/free/

---

## ⚠️ LƯU Ý QUAN TRỌNG

### ARM Architecture
```
❌ Một số Docker images KHÔNG HỖ TRỢ ARM:
  - SonarQube Community (chỉ x86)
  - Một số Kafka images

✅ Đã hỗ trợ ARM:
  - PostgreSQL (postgres:16-alpine)
  - Redis (redis:7.2-alpine)
  - Python/FastAPI (python:3.11-slim)
  - Node.js/Next.js (node:20-alpine)
  - Prometheus + Grafana
  - Apache Kafka (kafka:3.6.1)
```

---

## 🚀 SETUP NHANH

### 1. Đăng Ký Oracle Cloud (5 phút)

1. Vào https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Điền thông tin (cần thẻ VISA/Mastercard để verify, KHÔNG trừ tiền)
4. Chọn region gần nhất (Singapore hoặc Japan)

### 2. Tạo ARM Instance (10 phút)

**Spec khuyến nghị cho MediAI:**
```yaml
Instance Configuration:
  Shape: VM.Standard.A1.Flex
  OCPUs: 2 (hoặc 4 nếu muốn)
  RAM: 12GB (hoặc 24GB nếu dùng 4 OCPU)
  OS: Ubuntu 22.04 (ARM64)
  Boot Volume: 100GB
  Network: Assign public IP
```

**Steps:**
1. Compute → Instances → Create Instance
2. Chọn image: Canonical Ubuntu 22.04 (aarch64)
3. Chọn shape: VM.Standard.A1.Flex
4. Configure OCPUs: 2, RAM: 12GB
5. Add SSH key (generate hoặc paste public key)
6. Create instance

### 3. Cấu Hình Security (5 phút)

**Mở ports cần thiết:**

```bash
# SSH vào instance
ssh ubuntu@YOUR_PUBLIC_IP

# Update firewall rules
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Oracle Cloud Console: Networking → Security Lists
# Add Ingress Rules:
#   - Port 80 (HTTP)
#   - Port 443 (HTTPS)
#   - Port 8000 (API - optional, for testing)
```

### 4. Install Docker (ARM-compatible) (10 phút)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (ARM64)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify
docker --version
docker compose version

# Logout and login again for docker group
exit
ssh ubuntu@YOUR_PUBLIC_IP
```

### 5. Deploy MediAI (15 phút)

```bash
# Clone repository
cd /opt
sudo mkdir mediai-production
sudo chown ubuntu:ubuntu mediai-production
git clone https://github.com/yourusername/MediAI.git mediai-production
cd mediai-production

# Create environment file
cp .env.example .env.production
nano .env.production  # Edit với production values

# Build ARM-compatible images
docker compose build

# Start core services only (no learning features initially)
docker compose up -d

# Check status
docker compose ps
docker compose logs -f api

# Test
curl http://localhost:8000/health
```

---

## 🔧 ARM-Specific Adjustments

### Dockerfile Modifications

**api/Dockerfile (ARM-compatible):**
```dockerfile
# Use ARM64-compatible base image
FROM python:3.11-slim

# Rest remains the same...
```

**Verify multi-arch support:**
```bash
# Check if image supports ARM
docker manifest inspect postgres:16-alpine | grep arm64
docker manifest inspect redis:7.2-alpine | grep arm64
```

### Docker Compose for ARM

**Already ARM-compatible:**
- ✅ `docker-compose.yml` (postgres, redis, api)
- ✅ `docker-compose.learning.yml` (kafka, timescaledb)
- ⚠️ `docker-compose.monitoring.yml` (prometheus, grafana OK; sonarqube NO)

**Fix for SonarQube:**
```yaml
# Remove SonarQube hoặc replace với alternative
# SonarQube Community không hỗ trợ ARM
# Alternative: SonarCloud (cloud-based, free tier)
```

---

## 💰 CHI PHÍ SO SÁNH

| Provider | RAM | CPU | Disk | Cost/month |
|----------|-----|-----|------|------------|
| **Oracle Cloud Free** | 24GB | 4 cores (ARM) | 200GB | **$0 FOREVER** ✅ |
| Hetzner CPX21 | 4GB | 2 cores (x86) | 40GB | €8.46 (~$9) |
| DigitalOcean Basic | 4GB | 2 cores (x86) | 80GB | $24 |
| Railway (paid) | 8GB | 8 cores (x86) | 100GB | ~$20 |

**Winner: Oracle Cloud** 🏆

---

## 📊 RESOURCE ALLOCATION (24GB RAM)

### Conservative (Recommended)

```yaml
Instance 1 (12GB RAM, 2 OCPU):
  Core Services:
    - PostgreSQL: 2GB
    - Redis: 512MB
    - FastAPI: 2GB
    - Next.js (build): 1GB
    - Nginx: 128MB

  Learning Features:
    - Kafka: 1GB
    - TimescaleDB: 1GB (separate instance)
    - Jupyter: 1GB
    - Stream processor: 512MB

  Monitoring:
    - Prometheus: 1GB
    - Grafana: 512MB

  Total: ~11GB (1GB buffer)
```

### Aggressive (Use all 24GB)

```yaml
Create 2 instances:
  Instance 1 (12GB): Production services
  Instance 2 (12GB): Development + monitoring

OR single instance with all services
```

---

## 🚨 COMMON ISSUES

### Issue 1: Out of capacity
```
Error: Out of host capacity

Solution: Try different Availability Domain
- Compute → Instances → Edit → Change AD
- Or try different region (Seoul, Mumbai)
```

### Issue 2: ARM image not found
```
Error: no matching manifest for linux/arm64

Solution: Specify platform or use ARM-compatible image
docker build --platform linux/arm64 -t myimage .
```

### Issue 3: Performance slower than x86
```
ARM A1 is competitive but some workloads slower

Solution:
- Use 4 OCPUs instead of 2
- Enable compilation optimizations
- Use ARM-optimized libraries
```

---

## ✅ VERIFICATION CHECKLIST

After setup complete:

- [ ] Oracle Cloud account created
- [ ] VM.Standard.A1.Flex instance running (12-24GB RAM)
- [ ] Public IP assigned and accessible
- [ ] Firewall rules configured (ports 80, 443, 22)
- [ ] Docker + Docker Compose installed (ARM64)
- [ ] MediAI cloned to `/opt/mediai-production`
- [ ] Core services running (postgres, redis, api)
- [ ] Health check passes: `curl http://PUBLIC_IP:8000/health`
- [ ] Optional: SSL certificate (Let's Encrypt)
- [ ] Optional: Domain name pointed to public IP

---

## 🎯 NEXT STEPS

1. **Domain & SSL:**
   ```bash
   # Install Certbot
   sudo snap install --classic certbot

   # Get SSL certificate
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Enable Learning Features:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.learning.yml \
     --profile streaming --profile timeseries up -d
   ```

3. **Setup Monitoring:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml \
     --profile monitoring up -d
   ```

4. **Automated Backups:**
   ```bash
   # Database backup script
   crontab -e
   # Add: 0 2 * * * /opt/mediai-production/scripts/backup.sh
   ```

---

## 📚 RESOURCES

- Oracle Cloud Docs: https://docs.oracle.com/en-us/iaas/Content/home.htm
- ARM Docker Images: https://hub.docker.com/search?architecture=arm64
- Free Tier FAQ: https://www.oracle.com/cloud/free/faq.html
- Community: https://www.reddit.com/r/oraclecloud/

---

**Document Version:** 1.0
**Last Updated:** 2024-12-16
**Cost:** $0/month VĨNH VIỄN ✅
