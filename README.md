# ⚡ SmartMeterSim: Smart Meter Monitoring with AWS IoT

## Overview
**SmartMeterSim** is an **IoT-based smart meter simulator** that streams **real-time energy consumption data** to AWS IoT Core using **MQTT**. This data is then **visualized in a real-time dashboard**.  

### **Features**
- **Simulated Smart Meter** → Publishes real-time energy data  
- **AWS IoT Core Integration** → Secure MQTT communication  
- **Dashboard** → Live visualization of energy consumption  
- **Scalable Architecture** → Can integrate with real smart meters in future  

### **Industry Applications**
- Smart Grid            # Grid monitoring, energy analytics
- Industrial IoT(IIoT)  # IoT energy metering in factories
- Home Automation       # Integration with smart home systems
- EV Charging           # Energy usage tracking for EV charging stations

## **Project Structure**
```
📂 SmartMeterSim/
├── 📂 data
│   ├── smart_meter_data.csv   # Simulated energy meter readings
├── 📂 src
│   ├── mqtt_publisher.py      # Simulates a smart meter & sends data to AWS IoT
│   ├── mqtt_subscriber.py     # Receives & processes real-time meter data 
├── 📂 demo
│   ├── dashboard.py           # Web app for real-time visualization
├── 📂 config
│   ├── aws_iot_config.json    # AWS endpoint & MQTT topic config
│   └── secrets.toml           # AWS credentials (gitignored)
└── 📂 auth/                   # IoT device & root/IAM user certs files: policy, cert, ca, key (gitignored)
``` 

## 🔧 **Setup & Installation**

### **Clone the repository**  

```bash
git clone https://github.com/afondiel/SmartMeterSim.git
cd SmartMeterSim
```

### **Install dependencies**  
```bash
pip install -r requirements.txt
```

### **Set up AWS IoT Core & Credentials**
> [!IMPORTANT] \
> AWS Account with **AWS IoT Core** (Mandatory!)

1️⃣ **Using AWS Management Console** 

1. Go to AWS IoT Core -> Connect (Make sure you're connected to AWS IoT) 
```bash
ping <your-aws-iot-account>-ats.iot.<region>.amazonaws.com
```
2. Create a new **Thing** named `smartMeter01` -> Next
3. Choose a platform and device SDK (e.g.: Linux and Python)   
4. Download connection kit -> Next 
5. Instead of 'Run connection kit' -> unzip and copy into `auth/` folder

- Upate your `smartMeter01-Policy.json`and replace all the default config with the following:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:Connect",
                "iot:Publish",
                "iot:Receive",
                "iot:Subscribe"
            ],
            "Resource": ["arn:aws:iot:YOUR_REGION:YOUR_AWS_ACCOUNT_ID:topic/smartmeter/data"]
        }
    ]
}
```

2️⃣ **Using AWS IoT CLI**

Here's a full AWS IoT setup script [setup_aws_iot.sh](setup_aws_iot.sh) to spare you some time 

Run the script:
```bash
chmod +x setup_aws_iot.sh
./setup_aws_iot.sh
```
For Windows user you can run each instruction starting by `aws <command>...` inside your cmd/PS (If you encounter any problem, please raise an issue)

- If you haven't AWS IoT CLI installed yet, check out this [guide](https://github.com/afondiel/awesome-aws-iot-edge-cli).

Finally:

- Update `config/aws_iot_config.toml` with your AWS settings.
```bash
cp aws_iot_config_temp aws_iot_config.json  # Create a copy
nano aws_iot_config  # Edit and add your credentials
``` 
- Update `config/secrets.toml` with your AWS settings.
```bash
cp secrets-template.toml secrets.toml  # Create a copy
nano secrets.toml  # Edit and add your credentials
``` 

## Getting Started

### 📌 **How It Works**
1. **Reads** energy consumption data from CSV.  
2. **Simulates real-time readings** → Sends data to AWS IoT via MQTT.  
3. **Subscribes** to AWS IoT Core → Receives & logs energy data.  
4. **Displays** live consumption trends dashboard**.  

### 🔒 **Security**
- **TLS Encryption for MQTT Communication**  
- **AWS IoT Policies for Controlled Access**  
- **Environment Secrets for Credential Protection**  

### Usage

1️⃣ **Run the Smart Meter Simulator**  
```bash
python src/mqtt_publisher.py
```

2️⃣ **Start the Dashboard**  
- Gradio:

```bash
python demo/gradio_app.py
```

- Streamlit:

```bash
streamlit run demo/streamlit_app.py
```

3️⃣ **All-in: run all at once**
```bash
chmod +x startup.sh
./startup.sh
```

## Contributing 

Your contributions are welcomed!

**🚀 Future Roadmap**:
- IoT Smart Meter Simulator (You are here!)
- Scaling & Cloud-to-Edge Transition
- Real Smart Meter Integration (in your software stack)

## **📩 Contact**
🔗 Connect via [LinkedIn](https://linkedin.com/in/afonso-diela) or reach out for **IoT consulting & smart metering solutions**!
