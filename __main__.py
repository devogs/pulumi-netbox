# __main__.py (Version with DCIM Integration)

import pulumi
import pulumi_netbox as netbox

# Import logic modules (they are .py files inside the 'infra' package)
from infra.organization import (
    create_tenant_groups, create_tenants, 
    create_regions, create_site_groups, create_sites, create_locations
)
from infra.ipam import (
    create_rirs, create_asns, create_vrfs, 
    create_aggregates, create_prefixes
)
from infra.dcim import ( # <-- NEW IMPORT
    create_manufacturers, create_device_roles, 
    create_device_types, create_devices
)
from infra.data_reader import read_yaml_data


# ---------------------------------
# 1. READ ALL DATA (Data Access Responsibility)
# ---------------------------------
# Load all YAML data files into simple Python dictionaries

# Organization Data
tenancy_data = read_yaml_data(['data', 'organization', 'tenancy.yaml'])
sites_locations_data = read_yaml_data(['data', 'organization', 'sites_locations.yaml'])

# IPAM Data
rirs_asns_data = read_yaml_data(['data', 'ipam', 'rirs_asns.yaml'])
vrfs_data = read_yaml_data(['data', 'ipam', 'vrfs.yaml'])
prefixes_data = read_yaml_data(['data', 'ipam', 'prefixes.yaml'])

# DCIM Data <-- NEW DATA LOAD
dcim_devices_data = read_yaml_data(['data', 'dcim', 'devices.yaml'])


# ---------------------------------
# 2. ORCHESTRATION: TENANCY (Groups -> Tenants)
# ---------------------------------

# 2.1 Create Tenant Groups
tenant_groups_outputs = create_tenant_groups(tenancy_data.get('tenant_groups', []))

# 2.2 Create Tenants (Depends on Tenant Groups outputs)
tenants = create_tenants(tenancy_data.get('tenants', []), tenant_groups_outputs)
# Store the CLAB Tenant ID Output for later site creation
clab_tenant_id_output = tenants['clab'].id # Tenants are resource objects, so .id is correct here


# ---------------------------------
# 3. ORCHESTRATION: IPAM (RIRs -> ASNs/Aggregates, VRFs -> Prefixes)
# ---------------------------------

# 3.1 Create RIRs. Must return a dictionary of Rir OBJECTS for dependency chain.
rir_resources = create_rirs(rirs_asns_data.get('rirs', []))

# 3.2 Create VRFs. Must return a dictionary of Vrf OBJECTS for dependency chain.
vrf_resources = create_vrfs(vrfs_data.get('vrfs', []))

# 3.3 Create Individual ASNs for eBGP routers (Passes Rir OBJECTS)
asns = create_asns(rirs_asns_data.get('asns', []), rir_resources)

# 3.4 Create Aggregates (Passes Rir OBJECTS)
aggregates = create_aggregates(prefixes_data.get('aggregates', []), rir_resources)

# 3.5 Create Prefixes (Passes Vrf OBJECTS)
prefixes = create_prefixes(prefixes_data.get('prefixes', []), vrf_resources)


# ---------------------------------
# 4. ORCHESTRATION: SITES (Groups/Regions -> Sites -> Locations)
# ---------------------------------

# 4.1 Create Regions
regions_outputs = create_regions(sites_locations_data.get('regions', []))

# 4.2 Create Site Groups
site_groups_outputs = create_site_groups(sites_locations_data.get('site_groups', []))

# 4.3 Create Sites (Depends on Site Groups outputs AND CLAB Tenant ID)
sites_outputs = create_sites(
    sites_locations_data.get('sites', []), 
    site_groups_outputs, 
    clab_tenant_id_output
)

# 4.4 Create Locations (Depends on Sites outputs)
locations = create_locations(sites_locations_data.get('locations', []), sites_outputs)


# ---------------------------------
# 5. ORCHESTRATION: DCIM (Foundation -> Devices) <-- NEW SECTION
# ---------------------------------

print("===================================")
print("5. ORCHESTRATION: DCIM")
print("===================================")

# 5.1 Create Manufacturers
manufacturer_resources = create_manufacturers(dcim_devices_data.get('manufacturers', []))

# 5.2 Create Device Roles
device_role_resources = create_device_roles(dcim_devices_data.get('device_roles', []))

# 5.3 Create Device Types (Depends on Manufacturers)
device_type_resources = create_device_types(
    dcim_devices_data.get('device_types', []), 
    manufacturer_resources
)

# 5.4 Create Device Instances (Requires many dependencies)
# We pass all necessary resource dictionaries to a single handler
device_resources = create_devices(
    dcim_devices_data.get('devices', {}),
    {
        'device_roles': device_role_resources,
        'device_types': device_type_resources,
        'sites': sites_outputs,       # From Section 4
        'locations': locations,       # From Section 4
        'tenants': tenants,           # From Section 2
        'asns': asns                  # From Section 3
    }
)


# ---------------------------------
# 6. EXPORTS (Outputs for verification) <-- RENAMED SECTION (formerly 5)
# ---------------------------------

# # Tenancy Exports (Reverted: assuming these functions return the ID Output directly)
# pulumi.export("TenantGroup_Devogs_ID", tenant_groups_outputs['devogs']) 
# pulumi.export("Tenant_CLAB_ID", clab_tenant_id_output)

# # Site Exports (Reverted: assuming these functions return the ID Output directly)
# pulumi.export("LabSiteID", sites_outputs['clab-host-laptop']) 
# pulumi.export("cEOSLocationName", locations['ceos-spine-leaf'].name)

# # IPAM Exports (Keeping the correct resource object structure)
# # pulumi.export("MgmtVRFID", vrf_resources['mgmt'].id) # Example export
# # pulumi.export("RirRFC6996ID", rir_resources['rfc6996'].id) # Example export
# # pulumi.export("MgmtPrefix", prefixes['172.22.0.0/16'].prefix) # Example export
# # pulumi.export("Spine1_ASN", asns[65001].asn) # Example export