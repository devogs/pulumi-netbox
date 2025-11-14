# infra/orchestration/organization.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any
# Import all atomic helpers
from infra.atomic.organization import (
    _create_single_tenant_group, _create_single_tenant, 
    _create_single_region, _create_single_site_group, 
    _create_single_site, _create_single_location
)


# --- Orchestration Tenant Groups and Tenants (Preserves original function signature) ---

def create_tenant_groups(group_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.TenantGroup]:
    """Responsibility: Orchestrate the creation of ALL TenantGroup resources."""
    print("-> Creating Tenant Groups...")
    created_groups = {}
    for group_data in group_data_list:
        group = _create_single_tenant_group(group_data) # Atomic call
        created_groups[group_data['slug']] = group
    return created_groups


def create_tenants(tenant_data_list: List[Dict[str, Any]], created_groups_outputs: Dict[str, netbox.TenantGroup]) -> Dict[str, netbox.Tenant]:
    """Responsibility: Orchestrate the creation of ALL Tenant resources."""
    print("-> Creating Tenants...")
    created_tenants = {}
    for tenant_data in tenant_data_list:
        tenant = _create_single_tenant(tenant_data, created_groups_outputs) # Atomic call
        created_tenants[tenant_data['slug']] = tenant
    return created_tenants

# --- Orchestration Sites & Locations ---

def create_regions(region_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Region]:
    """Responsibility: Orchestrate the creation of ALL Region resources."""
    print("-> Creating Regions...")
    created_regions = {}
    for region_data in region_data_list:
        region = _create_single_region(region_data) # Atomic call
        created_regions[region_data['slug']] = region
    return created_regions


def create_site_groups(group_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.SiteGroup]:
    """Responsibility: Orchestrate the creation of ALL SiteGroup resources."""
    print("-> Creating Site Groups...")
    created_groups = {}
    for group_data in group_data_list:
        group = _create_single_site_group(group_data) # Atomic call
        created_groups[group_data['slug']] = group
    return created_groups


def create_sites(site_data_list: List[Dict[str, Any]], site_group_resources: Dict[str, netbox.SiteGroup], clab_tenant_id_output: Output) -> Dict[str, netbox.Site]:
    """Responsibility: Orchestrate the creation of ALL Site resources."""
    print("-> Creating Sites...")
    created_sites = {}
    for site_data in site_data_list:
        site = _create_single_site(site_data, site_group_resources, clab_tenant_id_output) # Atomic call
        created_sites[site_data['slug']] = site
    return created_sites


def create_locations(location_data_list: List[Dict[str, Any]], site_resources: Dict[str, netbox.Site]) -> Dict[str, netbox.Location]:
    """Responsibility: Orchestrate the creation of ALL Location resources."""
    print("-> Creating Locations...")
    created_locations = {}
    for location_data in location_data_list:
        location = _create_single_location(location_data, site_resources) # Atomic call
        created_locations[location_data['slug']] = location
    return created_locations