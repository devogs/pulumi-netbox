# infra/orchestration/dcim.py (Corrected)

import pulumi_netbox as netbox
from typing import Dict, List, Any
# Import atomic helpers
from infra.atomic.dcim import (
    _create_single_manufacturer, _create_single_device_role, 
    _create_single_device_type, _create_single_interface_template, 
    create_single_device
)


# ===============================================
# 1. FOUNDATIONAL ORCHESTRATION 🔁
# ===============================================
# (Manufacturers, Roles, and Device Types remain unchanged)

def create_manufacturers(manufacturer_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Manufacturer]:
    """Responsibility: Orchestrate the creation of ALL Manufacturer resources."""
    print("-> Creating Manufacturers...")
    created_manufacturers = {}
    for data in manufacturer_data_list:
        manufacturer = _create_single_manufacturer(data)
        created_manufacturers[data['slug']] = manufacturer
    return created_manufacturers


def create_device_roles(role_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.DeviceRole]:
    """Responsibility: Orchestrate the creation of ALL Device Role resources."""
    print("-> Creating Device Roles...")
    created_roles = {}
    for data in role_data_list:
        role = _create_single_device_role(data)
        created_roles[data['slug']] = role
    return created_roles


def create_device_types(type_data_list: List[Dict[str, Any]], manufacturer_resources: Dict[str, netbox.Manufacturer]) -> Dict[str, netbox.DeviceType]:
    """Responsibility: Orchestrate the creation of ALL Device Type resources."""
    print("-> Creating Device Types...")
    created_device_types = {}
    for type_data in type_data_list:
        device_type = _create_single_device_type(type_data, manufacturer_resources)
        created_device_types[type_data['slug']] = device_type
    return created_device_types


def create_interface_templates(type_data_list: List[Dict[str, Any]], device_type_resources: Dict[str, netbox.DeviceType]):
    """Responsibility: Orchestrate the creation of ALL Interface Templates."""
    print("-> Creating Interface Templates...")
    for type_data in type_data_list:
        device_type_slug = type_data['slug'] # <-- Grab the simple string slug from the input data
        device_type_resource = device_type_resources[device_type_slug]
        
        for interface_data in type_data.get('interfaces', []):
            # Pass the simple string slug to the atomic function
            _create_single_interface_template(interface_data, device_type_resource, device_type_slug) 


# ===============================================
# 2. DEVICE INSTANCE ORCHESTRATION 🔁
# ===============================================

def create_devices(device_data_dict: Dict[str, Any], all_deps: Dict[str, Any]) -> Dict[str, netbox.Device]:
    """
    Responsibility: Orchestrate the creation of all Device instances by looping 
    over the data and calling the atomic creation function.
    """
    print("-> Creating Devices...")
    created_devices = {}

    for device_name, data in device_data_dict.items():
        device = create_single_device(device_name, data, all_deps)
        created_devices[device_name] = device
        
    return created_devices