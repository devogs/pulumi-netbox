# __main__.py (Refactored for Orchestration/Atomic SOLID Structure)

# import pulumi
# import pulumi_netbox as netbox
# from pulumi import Output
# from typing import Dict, List, Any

# ===============================================
# IMPORT ORCHESTRATION LOGIC (The "Looping" Layer)
# ===============================================

# 1. Organization Orchestration
from infra.orchestration.organization import (
    create_tenant_groups, create_tenants,
    create_regions, create_site_groups, create_sites, create_locations
)

# 2. IPAM Orchestration
from infra.orchestration.ipam import (
    create_rirs, create_asns, create_vrfs,
    create_aggregates, create_prefixes
)

# 3. DCIM Orchestration
from infra.orchestration.dcim import (
    create_manufacturers, create_device_roles,
    create_device_types, create_interface_templates, create_devices
)

# 4. Utility Import (Assuming utils/data_reader.py)
from utils.data_reader import read_yaml_data
from utils.exports import run_exports


# ---------------------------------
# 1. READ ALL DATA 💾
# ---------------------------------
# Load all YAML data files into simple Python dictionaries

# Organization Data
tenancy_data = read_yaml_data(['data', 'organization', 'tenancy.yaml'])
sites_locations_data = read_yaml_data(['data', 'organization', 'sites_locations.yaml'])

# IPAM Data
rirs_asns_data = read_yaml_data(['data', 'ipam', 'rirs_asns.yaml'])
vrfs_data = read_yaml_data(['data', 'ipam', 'vrfs.yaml'])
prefixes_data = read_yaml_data(['data', 'ipam', 'prefixes.yaml'])

# DCIM Data
dcim_data = read_yaml_data(['data', 'dcim', 'devices.yaml'])


# ---------------------------------
# 2. ORCHESTRATION: ORGANIZATION 🏢
# ---------------------------------
# Ensure correct dependency order: Groups -> Tenants | Groups -> Sites -> Locations

# 2.1 Create Tenant Groups (Returns map of slug -> full resource object)
tenant_groups = create_tenant_groups(tenancy_data.get('tenant_groups', []))

# 2.2 Create Tenants (Depends on Tenant Groups)
tenants = create_tenants(tenancy_data.get('tenants', []), tenant_groups)

# Get the specific Tenant resource needed for Site creation
clab_tenant_resource = tenants['clab']
clab_tenant_id_output = clab_tenant_resource.id.apply(lambda id: int(id))

# 2.3 Create Regions
regions = create_regions(sites_locations_data.get('regions', []))

# 2.4 Create Site Groups
site_groups = create_site_groups(sites_locations_data.get('site_groups', []))

# 2.5 Create Sites (Depends on Site Groups AND CLAB Tenant ID)
sites_outputs = create_sites(
    sites_locations_data.get('sites', []),
    site_groups,
    clab_tenant_id_output
)

# 2.6 Create Locations (Depends on Sites)
locations = create_locations(sites_locations_data.get('locations', []), sites_outputs)


# ---------------------------------
# 3. ORCHESTRATION: IPAM 🌐
# ---------------------------------
# Ensure correct dependency order: RIRs -> ASNs/Aggregates | VRFs -> Prefixes

# 3.1 Create RIRs
rir_resources = create_rirs(rirs_asns_data.get('rirs', []))

# 3.2 Create VRFs
vrf_resources = create_vrfs(vrfs_data.get('vrfs', []))

# 3.3 Create Individual ASNs (Passes Rir resources for dependency)
asns = create_asns(rirs_asns_data.get('asns', []), rir_resources)

# 3.4 Create Aggregates (Passes Rir resources for dependency)
aggregates = create_aggregates(prefixes_data.get('aggregates', []), rir_resources)

# 3.5 Create Prefixes (Passes Vrf resources for dependency)
prefixes = create_prefixes(prefixes_data.get('prefixes', []), vrf_resources)


# ---------------------------------
# 4. ORCHESTRATION: DCIM 💻
# ---------------------------------
# Ensure correct dependency order: Manuf -> Roles -> Types -> Interfaces -> Devices

# 4.1 Create Manufacturers
manufacturers = create_manufacturers(dcim_data.get('manufacturers', []))

# 4.2 Create Device Roles
device_roles = create_device_roles(dcim_data.get('device_roles', []))

# 4.3 Create Device Types (Depends on Manufacturers)
device_types = create_device_types(dcim_data.get('device_types', []), manufacturers)

# 4.4 Create Interface Templates (Depends on Device Types, honors SRP)
create_interface_templates(dcim_data.get('device_types', []), device_types)

# 4.5 Create Devices (The main orchestration point for all resources)

# Collect ALL dependencies into one dictionary for the device creation function
all_dependencies = {
    'manufacturers': manufacturers,
    'device_roles': device_roles,
    'device_types': device_types,
    'sites': sites_outputs,
    'locations': locations,
    'tenants': tenants,
    'asns': asns
    # Note: IPAM resources (VRFs/Prefixes) are not direct dependencies of netbox.Device,
    # but are needed for the next step (Interfaces/IPs).
}
device_resources = create_devices(dcim_data.get('devices', {}), all_dependencies)


# ---------------------------------
# 5. EXPORTS 🚀
# ---------------------------------

run_exports(
    tenants=tenants,
    vrf_resources=vrf_resources,
    sites=sites_outputs,
    devices=device_resources
)
