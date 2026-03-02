# 🛡️ ML Random Forest DDoS Detection System

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue)](https://reactjs.org/)
[![Zeek](https://img.shields.io/badge/Zeek-8.1.1-orange)](https://zeek.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

A complete **DDoS SYN Flood detection and mitigation system** using **Zeek** for network monitoring, **Machine Learning (Random Forest)** for real‑time detection, and **iptables** for inline defense. The project includes three virtual machines (Kali – attacker, Ubuntu Server – IDS, Ubuntu Desktop – victim) and two real‑time dashboards (IDS and victim) built with **FastAPI** and **React**.

---

## ✨ Key Features

- ✅ **Zeek 8.1.1** captures all traffic between attacker and victim.
- ✅ **Automated feature engineering** from `conn.log` (3–5 second windows).
- ✅ **Random Forest model** trained with GridSearchCV, achieving **F1‑score > 0.96**.
- ✅ **Real‑time detection** with confidence threshold and automatic defense activation.
- ✅ **Inline mitigation** using iptables rate limiting and SYN cookies when consecutive attacks are detected.
- ✅ **Two interactive dashboards** (IDS and victim) displaying live metrics, top source IPs, firewall rules, and system health.
- ✅ All three VMs have **Internet access**; the IDS acts as a router and sensor (no traffic bypass).

---

## 🏗️ System Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Kali Linux    │         │  Ubuntu Server  │         │  Ubuntu Victim  │
│   (Attacker)    │         │      (IDS)      │         │    (Victim)     │
│  172.16.212.10  │         │  172.16.212.1   │         │  172.16.213.20  │
│                 │         │  172.16.213.1   │         │                 │
│                 │         │  172.16.113.x   │         │                 │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │        ens33              │        ens37              │
         ├───────────────────────────┼───────────────────────────┤
         │       VMnet1              │       VMnet2              │
         │   172.16.212.0/24         │   172.16.213.0/24         │
         │                           │                           │
         │                           │   ens38                   │
         │                           ├───────────────────────────┤
         │                           │        VMnet8 (NAT)       │
         │                           │       to Internet         │
         └───────────────────────────┴───────────────────────────┘
```

- **Kali** generates normal traffic (HTTP, Apache Bench) and SYN flood attacks (`hping3 --rand-source`).
- **IDS** runs Zeek on `ens33`, processes flows, predicts attacks, and dynamically updates iptables.
- **Victim** hosts a simple web server and exposes a monitoring API (CPU, RAM, network, active connections).

---

## 🧰 Technology Stack

| Component             | Technology |
|-----------------------|------------|
| Network Monitoring    | Zeek 8.1.1 |
| Machine Learning      | Python 3.11, scikit-learn (Random Forest, GridSearchCV) |
| Backend API           | FastAPI, Uvicorn |
| Frontend              | React + TypeScript, Vite, Recharts |
| Firewall              | iptables (inline) |
| Virtualization        | VMware Workstation (VMnet1, VMnet2, VMnet8) |
| Operating Systems     | Kali Linux, Ubuntu Server 22.04, Ubuntu Desktop 22.04 |

---

## 📁 Repository Structure

```
ML-randomforest-ddos-detection/
├── zeek_flow/                     # Core Zeek config and Python scripts
│   ├── config/
│   │   └── local.zeek              # Optimized Zeek configuration
│   ├── scripts/
│   │   ├── 01_start_zeek.sh
│   │   ├── 02_generate_traffic_kali.sh   # Run on Kali
│   │   ├── 03_stop_zeek.sh
│   │   ├── 04_feature_engineering.py
│   │   ├── 05_train_model.py
│   │   └── 06_detect_live.py
│   ├── data/                        # (git‑ignored) logs, datasets
│   └── model/                        # (git‑ignored) trained models
├── backend_ids/                      # FastAPI backend for IDS dashboard
│   ├── app/
│   └── requirements.txt
├── frontend_ids/                      # React frontend for IDS dashboard
│   ├── src/
│   └── package.json
├── backend_victim/                    # FastAPI backend for victim dashboard
│   ├── app/
│   └── requirements.txt
├── frontend_victim/                    # React frontend for victim dashboard
│   ├── src/
│   └── package.json
├── docs/                               # Screenshots, diagrams (optional)
├── .gitignore
└── README.md
```

---

## 🚀 Installation & Usage

### Hardware / VM Requirements
- Three VMs with at least **2 GB RAM** and **20 GB disk** each.
- VMware Workstation with pre‑configured VMnet networks as shown above.

### 1. Network Configuration on IDS (Ubuntu Server)

```bash
# Check interface names (must show ens33, ens37, ens38)
ip link show

# Edit netplan
sudo nano /etc/netplan/00-installer-config.yaml
```

Paste the following (adjust interface names if necessary):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      addresses: [172.16.212.1/24]
    ens37:
      addresses: [172.16.213.1/24]
    ens38:
      dhcp4: true
```

Apply and enable IP forwarding:

```bash
sudo netplan apply
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

### 2. Basic iptables Setup on IDS

Run the following commands to allow NAT and forwarding:

```bash
sudo iptables -t nat -A POSTROUTING -o ens38 -j MASQUERADE
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -i ens33 -o ens38 -j ACCEPT   # Kali → Internet
sudo iptables -A FORWARD -i ens37 -o ens38 -j ACCEPT   # Victim → Internet
sudo iptables -A FORWARD -i ens33 -o ens37 -j ACCEPT   # Kali → Victim
sudo iptables -A FORWARD -i ens37 -o ens33 -j ACCEPT   # Victim → Kali
```

(Optional) Save rules with `iptables-persistent`.

### 3. Configure Kali (Attacker)

- Static IP: `172.16.212.10/24`, gateway `172.16.212.1`, DNS `8.8.8.8`.
- Copy `zeek_flow/scripts/02_generate_traffic_kali.sh` to Kali and make it executable.

### 4. Configure Victim (Ubuntu Desktop)

- Static IP: `172.16.213.20/24`, gateway `172.16.213.1`, DNS `8.8.8.8`.
- Run a simple web server listening on port 80 (e.g., `python3 -m http.server 80` or install nginx).

### 5. Collect Training Data

**On IDS** (Terminal 1):
```bash
cd ~/zeek_flow
sudo ./scripts/01_start_zeek.sh        # Zeek runs in foreground
```

**On Kali** (Terminal 2):
```bash
cd /path/to/script
chmod +x 02_generate_traffic_kali.sh
./02_generate_traffic_kali.sh          # Runs 10 phases (normal 60s + attack 20s + cooldown)
```

**After Kali finishes, on IDS** (Terminal 3):
```bash
./scripts/03_stop_zeek.sh
```

### 6. Feature Engineering & Model Training

```bash
python3 scripts/04_feature_engineering.py   # Creates dataset.csv from conn.log
python3 scripts/05_train_model.py           # Trains Random Forest + GridSearch
```

Trained model and evaluation results are saved in the `model/` directory.

### 7. Real‑time Detection

**On IDS**:
```bash
sudo python3 scripts/06_detect_live.py
```

**On Kali** (to simulate an attack):
```bash
sudo hping3 -S -p 80 --flood --rand-source 172.16.213.20
```

The IDS will display alerts, and after two consecutive detections it will automatically enable defense (iptables rate limiting + SYN cookies). Check active rules with `sudo iptables -L FORWARD -v`.

### 8. Run the Dashboards (Optional)

**IDS Backend**:
```bash
cd backend_ids
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**IDS Frontend**:
```bash
cd frontend_ids
npm install
npm run dev
```

Open `http://<IDS_IP>:5173` to see the IDS dashboard.

Repeat similarly for the victim dashboard (run on the victim machine).

---

## 📊 Results

After training on 10 phases (~1000 windows), the Random Forest model achieves:

| Metric     | Value  |
|------------|--------|
| Accuracy   | 98.2%  |
| Precision  | 0.97   |
| Recall     | 0.96   |
| F1‑score   | 0.96   |
| AUC‑ROC    | 0.99   |

**Top 3 most important features**:
1. `failed_ratio` (proportion of failed connections with `S0`/`REJ` state)
2. `syn_connections`
3. `connections_per_second`

---

## 🧪 Quick Verification

```bash
# Is Zeek running?
ps aux | grep zeek

# List logs
ls -la ~/zeek_flow/data/

# View iptables rules
sudo iptables -L FORWARD -v

# Flush rules after demo
sudo iptables -F FORWARD
```

---

## 📝 License

This project is licensed under the **MIT License** – feel free to use, modify, and distribute.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Please open an issue first to discuss what you would like to change.

---
<img width="1030" height="500" alt="image" src="https://github.com/user-attachments/assets/7e40fe74-9427-4efb-9e0f-1d898f8a4a9e" />

<img width="1019" height="472" alt="image" src="https://github.com/user-attachments/assets/24285db4-8dbf-42df-9638-0fec428b52bc" />

<img width="1087" height="507" alt="image" src="https://github.com/user-attachments/assets/87ff5cb9-0fe0-4e1c-b1ba-874173dd5e08" />

## 📧 Contact

**Author**: conbobi  
**GitHub**: [https://github.com/conbobi](https://github.com/conbobi)  
**Email**: conbobi@gmail.com

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
