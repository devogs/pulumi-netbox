# utils/exports.py

import pulumi
from typing import Dict
# Import the NetBox resource types for cleaner type hints
from pulumi_netbox import Tenant, Vrf, Site, Device 

def run_exports(
    tenants: Dict[str, Tenant], 
    vrf_resources: Dict[str, Vrf], 
    sites: Dict[str, Site], 
    devices: Dict[str, Device]
):
    """
    Centralizes all pulumi.export calls using the final resource dictionaries
    from the orchestration layer.
    """
    
    print("-> Finalizing and Exporting Outputs...")

    # --- Organization Exports ---
    try:
        pulumi.export("TenantClabID", tenants['clab'].id)
    except KeyError:
        print("Warning: Tenant 'clab' not found for export.")

    try:
        # Assuming the site slug is 'clab-host-laptop'
        pulumi.export("LabSiteID", sites['clab-host-laptop'].id)
    except KeyError:
        print("Warning: Site 'clab-host-laptop' not found for export.")

    # --- IPAM Exports ---
    try:
        # Exporting the Mgmt VRF, as 'infra-vrf' was removed.
        pulumi.export("MgmtVRFID", vrf_resources['mgmt'].id) 
    except KeyError:
        print("Warning: VRF 'mgmt' not found for export.")
    
    # --- DCIM Exports ---
    try:
        pulumi.export("Spine1Name", devices['spine-1'].name)
        pulumi.export("Leaf2Type", devices['leaf-2'].device_type_id)
    except KeyError:
        print("Warning: Some devices were not found for export.")