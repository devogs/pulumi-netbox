# infra/atomic/dcim.py (Corrected)

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any

# ===============================================
# 1. ATOMIC CREATION HELPERS (STRICT SRP) 🏗️
# ===============================================

def _create_single_manufacturer(data: Dict[str, Any]) -> netbox.Manufacturer:
    """Creates a single Manufacturer resource."""
    return netbox.Manufacturer(data['slug'],
        name=data['name'],
        slug=data['slug']
    )

def _create_single_device_role(data: Dict[str, Any]) -> netbox.DeviceRole:
    """Creates a single Device Role resource."""
    return netbox.DeviceRole(data['slug'],
        name=data['name'],
        slug=data['slug'],
        color_hex=data['color']
    )

def _create_single_device_type(type_data: Dict[str, Any], manufacturer_resources: Dict[str, netbox.Manufacturer]) -> netbox.DeviceType:
    """Creates a single Device Type resource, handling Manufacturer dependency."""
    type_slug = type_data['slug']
    manufacturer_resource = manufacturer_resources[type_data['manufacturer_slug']]
    
    # Cast Manufacturer ID to integer output
    manufacturer_id_input = manufacturer_resource.id.apply(lambda id: int(id))

    return netbox.DeviceType(type_slug,
        manufacturer_id=manufacturer_id_input,
        model=type_data['model'],
        slug=type_slug,
        u_height=type_data['height_u'],
        is_full_depth=type_data['is_full_depth']
    )

def _create_single_interface_template(interface_data: Dict[str, Any], device_type_resource: netbox.DeviceType, device_type_slug: str):
    """
    Creates a single Interface Template resource, handling Device Type dependency.
    FIXED: Uses the simple string 'device_type_slug' instead of resource.slug.get().
    """
    interface_name = interface_data['name']
    
    # Use the simple string slug (passed from orchestrator) to form a unique Pulumi resource name
    interface_slug = f"{device_type_slug}-{interface_name}".lower().replace('-', '_')
    
    netbox.InterfaceTemplate(interface_slug,
        # Dependency: Cast Device Type ID to integer output
        device_type_id=device_type_resource.id.apply(lambda id: int(id)),
        name=interface_name,
        type=interface_data['type'],
        mgmt_only=interface_data.get('mgmt_only', False)
    )

# ===============================================
# 2. DEVICE INSTANCE ATOMIC LOGIC
# ===============================================

def _resolve_device_dependencies(data: Dict[str, Any], all_deps: Dict[str, Any]) -> Dict[str, Output]:
    """Helper function to resolve all required NetBox resource IDs for a single Device."""
    
    def to_int_id(resource):
        # Local helper to convert resource object ID to the required Output[int]
        return resource.id.apply(lambda id: int(id))

    return {
        'role_id': to_int_id(all_deps['device_roles'][data['device_role_slug']]),
        'device_type_id': to_int_id(all_deps['device_types'][data['device_type_slug']]),
        'site_id': to_int_id(all_deps['sites'][data['site_slug']]), 
        'location_id': to_int_id(all_deps['locations'][data['location_slug']]),
        'tenant_id': to_int_id(all_deps['tenants'][data['tenant_slug']]),
        'asn_id': to_int_id(all_deps['asns'][data['asn']]), 
    }


def create_single_device(device_name: str, data: Dict[str, Any], all_deps: Dict[str, Any]) -> netbox.Device:
    """
    Responsibility: Create ONLY a single Device instance (Atomic function).
    """
    
    # 1. Resolve all dependencies
    dep_ids = _resolve_device_dependencies(data, all_deps)
    
    # 2. Create the Device
    device = netbox.Device(device_name,
        name=device_name.upper(), 
        device_type_id=dep_ids['device_type_id'],
        role_id=dep_ids['role_id'],
        site_id=dep_ids['site_id'],
        location_id=dep_ids['location_id'],
        tenant_id=dep_ids['tenant_id'],
        asset_tag=device_name.upper(),
        status="active" 
    )
    
    return device