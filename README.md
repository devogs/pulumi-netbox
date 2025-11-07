### \# ⚙️ NetBox IaC Project with Pulumi (Python)

This project uses Pulumi to manage the NetBox infrastructure required for Containerlab-based network laboratory (Lab) environments.

-----

### 1\. Prerequisites

Before starting, ensure the following are installed on your machine:

  * **Pulumi CLI** (version 3.x or higher)
  * **Python** (version 3.9+)
  * **pip** and **venv** (included with Python)
  * **Access to a NetBox instance** (for the API token and URL).

### 2\. Getting Started (New Machine)

Follow these steps to clone, configure, and run the project on a new system.

#### 2.1 Clone the Repository

```bash
git clone https://your-git-repo/pulumi-netbox-project.git
cd pulumi-netbox-project
```

#### 2.2 Python Environment Setup

Since we ignore the `venv/` folder in Git, you must recreate the virtual environment and install dependencies.

```bash
# 1. Create the virtual environment
python3 -m venv venv

# 2. Activate the environment
source venv/bin/activate  # macOS / Linux
# OR
.\venv\Scripts\activate   # Windows

# 3. Install Python dependencies (Pulumi SDK, pulumi-netbox, etc.)
pip install -r requirements.txt
```

#### 2.3 Install Pulumi Providers

This command reads the `Pulumi.yaml` file and downloads the necessary provider binaries (in our case, the bridged NetBox Terraform provider `e-breuninger/netbox@5.0.0`).

```bash
pulumi install
```

### 3\. Stack Management and Configuration

The project uses **Stacks** to separate environments (`lab`, `dev`, etc.).

#### 3.1 Select Your Stack

Select or create the stack you intend to use (e.g., the dedicated `lab` stack).

```bash
# To select an existing stack (e.g., 'lab')
pulumi stack select lab

# OR, to create a new stack (e.g., 'staging')
# pulumi stack init staging
```

#### 3.2 Configure NetBox Credentials

This is the most critical security step. You must configure your NetBox server URL and API Token **for this specific stack**:

```bash
# 1. Configure the URL (Non-Secret)
pulumi config set netbox:serverUrl https://your-netbox.domain.com

# 2. Configure the API Token (HIGHLY SECRET - ENCRYPTED)
# Pulumi will prompt you to enter the value, which it will then encrypt.
pulumi config set --secret netbox:apiToken
```

> **Security Note:** If the repository was encrypted with a master passphrase during its first use, you might need to enter that passphrase to access the Pulumi configuration.

### 4\. Deployment

You are now ready to deploy or update the infrastructure.

```bash
# Preview the planned changes
pulumi preview

# Deploy the changes to NetBox
pulumi up
```