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
   git clone https://github.com/yugabyte/cloud-resource-cleanup.git
