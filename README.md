# DDoS Attack Detection in SD-IoT Network Using Machine Learning

## Overview

This project implements a Machine Learning-based Intrusion Detection System (IDS) for detecting and mitigating Distributed Denial-of-Service (DDoS) attacks in a Software Defined IoT (SD-IoT) network.

The system combines Software Defined Networking (SDN) with Machine Learning to monitor network traffic, classify malicious flows, and automatically mitigate attacks through the Ryu SDN Controller.

The project was developed and tested on **Ubuntu 20.04** using **Mininet**, **Open vSwitch**, and the **Ryu SDN Controller**.

---

## Objectives

- Build an SDN-based Intrusion Detection System.
- Detect DDoS attacks in real time using Machine Learning.
- Monitor OpenFlow traffic through the Ryu Controller.
- Simulate TCP, UDP, and ICMP flooding attacks.
- Capture and analyze network packets.
- Extract network traffic features.
- Automatically mitigate malicious traffic using OpenFlow rules.
- Evaluate the effectiveness of different Machine Learning algorithms.

---

## Technologies Used

### Programming Language

- Python 3

### Software Defined Networking

- Ryu SDN Controller
- Mininet
- Open vSwitch
- OpenFlow 1.3

### Machine Learning

- Scikit-learn
- Random Forest
- Decision Tree
- Pandas
- NumPy

### Network Analysis

- Wireshark
- Scapy
- hping3

### Operating System

- Ubuntu 20.04 LTS

---

## Project Structure

```
DDoS-Attack-Detection-in-SD-IoT-Network-Using-Machine-Learning/

├── controller/
├── topology/
├── scripts/
├── dataset/
├── models/
├── screenshots/
├── docs/
├── README.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

---

## Project Workflow

1. Create the SD-IoT network topology using Mininet.
2. Connect switches with the Ryu SDN Controller.
3. Generate normal network traffic.
4. Launch DDoS attacks using hping3.
5. Capture packets using Wireshark.
6. Extract traffic features.
7. Train Machine Learning models.
8. Detect malicious traffic.
9. Install OpenFlow rules to block attack traffic.
10. Continue monitoring network activity.

---

## Repository Contents

### controller/

Contains the Ryu SDN controller responsible for:

- Flow monitoring
- Feature extraction
- Traffic classification
- DDoS mitigation
- OpenFlow rule installation

### topology/

Contains Mininet topology files used for network simulation.

### scripts/

Contains shell scripts for:

- DDoS attack generation
- Traffic capture
- Network testing

### dataset/

Contains packet captures and datasets used during the project.

### models/

Contains information about the Machine Learning models used for attack detection.

### screenshots/

Contains screenshots of:

- Mininet topology
- Controller output
- Wireshark packet capture
- Attack detection
- Evaluation results

### docs/

Project documentation including architecture, workflow, dataset description, and future scope.

---

## Machine Learning

The project evaluates two supervised learning algorithms:

- Random Forest
- Decision Tree

The models classify network traffic into:

- Normal Traffic
- DDoS Attack

Performance was evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score

---

## Installation

### Clone the repository

```bash
git clone https://github.com/prajwalhk560-cyber/DDoS-attack-detection-in-SD-IOT-Network-using-Machine-Learning.git
```

### Move into the project directory

```bash
cd DDoS-attack-detection-in-SD-IOT-Network-using-Machine-Learning
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Start the Ryu Controller

```bash
ryu-manager controller/detect_and_mitigate.py
```

### Launch the Mininet topology

```bash
sudo python3 topology/topology.py
```

### Generate attack traffic

```bash
bash scripts/attack.sh
```

---

## Results

The implemented system successfully:

- Simulated DDoS attacks within an SD-IoT environment.
- Captured and analyzed network traffic.
- Detected malicious traffic using Machine Learning.
- Applied mitigation by installing OpenFlow rules.
- Improved visibility into network behavior through packet-level analysis.

---

## Screenshots

The repository includes screenshots demonstrating:

- SDN Network Topology
- Ryu Controller Output
- Mininet Simulation
- Wireshark Packet Capture
- DDoS Detection
- Flow Statistics
- Machine Learning Evaluation

---

## Future Enhancements

- Deep Learning-based IDS
- XGBoost and LSTM models
- Real-time monitoring dashboard
- Cloud deployment
- Multi-controller SDN architecture
- Explainable AI (XAI)

---

## Learning Outcomes

Through this project, I gained practical experience in:

- Software Defined Networking (SDN)
- Ryu SDN Controller
- OpenFlow
- Mininet
- Open vSwitch
- DDoS attack simulation
- Machine Learning for Intrusion Detection
- Packet analysis using Wireshark
- Python automation
- Network traffic analysis
