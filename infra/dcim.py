# infra/dcim.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any

# --- Foundational Components ---

def create_manufacturers(manufacturer_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Manufacturer]:
    """Creates NetBox Manufacturers."""
    print("-> Creating Manufacturers...")
    created_manufacturers = {}
    for data in manufacturer_data_list:
        manufacturer = netbox.Manufacturer(data['slug'],
            name=data['name'],
            slug=data['slug']
        )
        created_manufacturers[data['slug']] = manufacturer
    return created_manufacturers


def create_device_roles(role_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.DeviceRole]:
    """Creates NetBox Device Roles."""
    print("-> Creating Device Roles...")
    created_roles = {}
    for data in role_data_list:
        role = netbox.DeviceRole(data['slug'],
            name=data['name'],
            slug=data['slug'],
            color=data['color']
        )
        created_roles[data['slug']] = role
    return created_roles


def create_device_types(type_data_list: List[Dict[str, Any]], manufacturer_resources: Dict[str, netbox.Manufacturer]) -> Dict[str, netbox.DeviceType]:
    """Creates NetBox Device Types and their Interfaces."""
    print("-> Creating Device Types and Interfaces...")
    created_device_types = {}
    
    for type_data in type_data_list:
        type_slug = type_data['slug']
        
        # 1. Get Manufacturer ID (Requires int() cast)
        manufacturer_resource = manufacturer_resources[type_data['manufacturer_slug']]
        manufacturer_id_input = manufacturer_resource.id.apply(lambda id: int(id))

        # 2. Create the Device Type
        device_type = netbox.DeviceType(type_slug,
            manufacturer_id=manufacturer_id_input,
            model=type_data['model'],
            slug=type_slug,
            u_height=type_data['height_u'],
            is_full_depth=type_data['is_full_depth']
        )
        created_device_types[type_slug] = device_type

        # 3. Create interfaces attached to the Device Type
        for interface_data in type_data.get('interfaces', []):
            interface_name = interface_data['name']
            interface_slug = f"{type_slug}-{interface_name}".lower().replace('-', '_')
            
            netbox.InterfaceTemplate(interface_slug,
                device_type_id=device_type.id.apply(lambda id: int(id)), # Dependency on Device Type ID
                name=interface_name,
                type=interface_data['type'],
                mgmt_only=interface_data.get('mgmt_only', False)
            )

    return created_device_types

# --- Device Instances ---

def create_devices(device_data_dict: Dict[str, Any], all_deps: Dict[str, Any]):
    """
    Creates individual Device instances.
    Requires: DeviceType, DeviceRole, Site, Location, Tenant, and ASN resources.
    """
    print("-> Creating Devices...")
    created_devices = {}
    
    # Extract necessary resource dictionaries for lookups
    device_roles = all_deps['device_roles']
    device_types = all_deps['device_types']
    sites = all_deps['sites']
    locations = all_deps['locations']
    tenants = all_deps['tenants']
    asns = all_deps['asns']

    for device_name, data in device_data_dict.items():
        # --- Resolve Dependencies (IDs are required as int outputs) ---
        
        # Device Type ID
        device_type_resource = device_types[data['device_type_slug']]
        device_type_id_input = device_type_resource.id.apply(lambda id: int(id))

        # Device Role ID
        device_role_resource = device_roles[data['device_role_slug']]
        device_role_id_input = device_role_resource.id.apply(lambda id: int(id))

        # Site ID
        site_resource = sites[data['site_slug']]
        site_id_input = site_resource.id.apply(lambda id: int(id))

        # Location ID
        location_resource = locations[data['location_slug']]
        location_id_input = location_resource.id.apply(lambda id: int(id))

        # Tenant ID (already a resolved ID output from org.py)
        tenant_resource = tenants[data['tenant_slug']]
        tenant_id_input = tenant_resource.id.apply(lambda id: int(id))
        
        # ASN ID (Lookup by ASN number, requires resource object)
        asn_resource = asns[data['asn']]
        asn_id_input = asn_resource.id.apply(lambda id: int(id))


        # --- Create the Device ---
        device = netbox.Device(device_name,
            name=device_name.upper(), # SP-1, LF-1, etc.
            device_type_id=device_type_id_input,
            device_role_id=device_role_id_input,
            site_id=site_id_input,
            location_id=location_id_input,
            tenant_id=tenant_id_input,
            asset_tag=device_name.upper(),
            # Status: 1 = Active
            status="1" 
        )
        
        # Store the created device resource
        created_devices[device_name] = device
        
        # --- Assign Primary IP Address (Placeholder for next step) ---
        # We will add the logic to create the Management IP and assign it here later.
        
    return created_devices