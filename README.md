# Energy Telemetry with AWS IoT

## Overview

A real-time analytics for energy meters using AWS IoT services. 

## Features

*   **Secure Data Collection:** Utilizes MQTT protocol and AWS IoT Core for secure data ingestion from simulated meters.
*   **Optimized Time-Series Storage:** Employs Amazon Timestream for efficient storage and retrieval of time-series data.
*   **Interactive Dashboards:** Leverages Amazon QuickSight to create customizable and real-time dashboards for data visualization.
*   **Predictive Analytics (Future):** Aims to integrate predictive analytics for forecasting consumption trends (future enhancement).
*   **Real-time Alerts (Future):** Plans to implement real-time alerts for proactive anomaly detection (future enhancement).

## Architecture

![Architecture Diagram (To be added)](./docs/architecture.png)

The key components of the Energy-Telemetry-AWS-IoT architecture are:

1.  **Simulated Energy Meters:** Simulated devices sending meter data via MQTT. (using AWS IoT Device Simulator)
2.  **AWS IoT Core:** Central hub for device connectivity, security, and data routing.
3.  **MQTT Protocol:** Standard messaging protocol for IoT devices.
4.  **AWS IoT Rules:** Routes incoming MQTT messages to a Lambda function.
5.  **AWS Lambda:** Processes and transforms the meter data.
6.  **Amazon Timestream:** Time-series database for storing meter readings.
7.  **Amazon QuickSight:** Business intelligence service for visualizing the data.

## Prerequisites

Before you begin, ensure you have the following:

*   An AWS account
*   AWS CLI installed and configured
*   Basic knowledge of AWS IoT Core, Lambda, Timestream, and QuickSight

## Getting Started

1.  **Clone the repository:**

    ```
    git clone https://github.com/afondiel/Energy-Telemetry-AWS-IoT.git
    cd Energy-Telemetry-AWS-IoT
    ```

2.  **Deploy AWS Infrastructure:**
    *This Project can be deploy using terraform/cloudformation*
    Follow the instructions in the `infra/README.md` file to deploy the required AWS resources.

     *(Create an infra folder and explain how to deploy your infra using terraform/cloudformation)*

3.  **Configure AWS IoT Device Simulator:**

    *   Create and configure simulated devices using the AWS IoT Device Simulator.
    *   Ensure the devices are configured to publish data to the correct MQTT topic (e.g., `grdf/meters/data`).

4.  **Configure AWS IoT Rule:**

    *   Create an AWS IoT rule to route messages from the MQTT topic to the Lambda function.

5.  **Configure AWS Lambda Function:**

    *   Update the Lambda function code (located in `lambda/`) with the correct Timestream database and table names.
    *   Deploy the Lambda function to AWS.

6.  **Create QuickSight Dashboard:**

    *   Connect QuickSight to the Timestream database.
    *   Create a new dataset based on the meter data table.
    *   Design interactive dashboards to visualize the meter data.

## Code Structure
```
Energy-Telemetry-AWS-IoT/
├── infra/               # Infrastructure as Code (Terraform or CloudFormation)
├── lambda/              # AWS Lambda function code
├── docs/                # Documentation (architecture diagrams, etc.)
├── scripts/             # Helper scripts
├── [README.md](http://readme.md/)            # This file

```

## Contributing

We welcome contributions to Energy-Telemetry-AWS-IoT! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

*   This project uses AWS IoT services.
*   Thanks to the AWS team for providing excellent documentation and support.
