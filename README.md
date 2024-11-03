# cloudResourcecleanup
A command-line utility for optimizing cloud resource management by identifying and removing unused resources. It integrates with Azure APIs to automate the cleanup process, achieving cost savings and efficient resource allocation. Supports flexible user inputs for resource identification and cleanup options.

# Get Started

## Prerequisites

- Python 3.x

### Required Python Packages

To interact with various cloud providers, the following Python packages are required:

- `boto3` (for AWS)
- `msrestazure` (for Azure)
- `azure-mgmt-compute` (for Azure)
- `azure-identity` (for Azure)
- `azure-mgmt-network` (for Azure)
- `google-cloud-compute` (for GCP)
- `google-api-python-client` (for GCP)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sprathamesh/cloudResourcecleanup.git
   cd cloud-resource-cleanup
   pip install -r requirements.txt

2. Set the other environment variables:
   ```bash
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AZURE_CREDENTIALS_TENANT_ID="your_tenant_id"
   export AZURE_CREDENTIALS_SUBSCRIPTION_ID="your_subscription_id"
   export AZURE_CREDENTIALS_CLIENT_SECRET="your_client_secret"
   export AZURE_CREDENTIALS_CLIENT_ID="your_client_id"
   export AZURE_RESOURCE_GROUP="your_resource_group"
   export SLACK_BOT_TOKEN="your_slack_bot_token"
   export INFLUXDB_TOKEN="your_influxdb_token"

### Script to Run:

1. To perform a dry run of the script and list all VMs across all clouds that have been created in the last 2 days:
   ```bash
   python crc.py --cloud all --resource vm --age "{'days': 2}" --dry_run
   
2.To delete all running AWS VMs that are older than 3 days and 12 hours.
   ```bash
   python crc.py --cloud aws --resource vm  --age "{'days': 3, 'hours': 12}"
