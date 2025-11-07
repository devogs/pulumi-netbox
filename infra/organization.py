# infra/organization.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any


def create_tenant_groups(group_data_list: List[Dict[str, Any]]):
    """
    Responsibility: Create ONLY TenantGroup resources.
    Returns: Dict[str, Output]: Map of slug to TenantGroup ID (Output).
    """
    print("-> Creating Tenant Groups...")
    created_groups = {}
    
    for group_data in group_data_list:
        group_slug = group_data['slug']
        group = netbox.TenantGroup(group_slug,
            name=group_data['name'],
            slug=group_slug,
            description=group_data.get('description')
        )
        created_groups[group_slug] = group.id 
        
    return created_groups


def create_tenants(tenant_data_list: List[Dict[str, Any]], created_groups_outputs: Dict[str, Output]):
    """
    Responsibility: Create ONLY Tenant resources.
    Handles dependency on Tenant Groups.
    Returns: Dict[str, netbox.Tenant]: Map of slug to Tenant resource object.
    """
    print("-> Creating Tenants...")
    created_tenants = {}
    
    for tenant_data in tenant_data_list:
        tenant_slug = tenant_data['slug']
        group_slug_ref = tenant_data.get('group_slug')
        
        # Dependency resolution using the ID Output from the first function
        group_id_output = created_groups_outputs.get(group_slug_ref)
        
        tenant = netbox.Tenant(tenant_slug,
            name=tenant_data['name'],
            slug=tenant_slug,
            description=tenant_data.get('description'),
            group_id=group_id_output 
        )
        created_tenants[tenant_slug] = tenant
        
    return created_tenants

# --- Functions for Sites & Locations (Same SRP Application) ---

def create_regions(region_data_list: List[Dict[str, Any]]):
    """
    Responsibility: Create ONLY Region resources.
    Returns: Dict[str, Output]: Map of slug to Region ID (Output).
    """
    print("-> Creating Regions...")
    created_regions = {}
    for region_data in region_data_list:
        region_slug = region_data['slug']
        region = netbox.Region(region_slug,
            name=region_data['name'],
            slug=region_slug,
            description=region_data.get('description')
        )
        created_regions[region_slug] = region.id
    return created_regions


def create_site_groups(group_data_list: List[Dict[str, Any]]):
    """
    Responsibility: Create ONLY SiteGroup resources.
    Returns: Dict[str, Output]: Map of slug to SiteGroup ID (Output).
    """
    print("-> Creating Site Groups...")
    created_groups = {}
    for group_data in group_data_list:
        group_slug = group_data['slug']
        group = netbox.SiteGroup(group_slug,
            name=group_data['name'],
            slug=group_slug,
            description=group_data.get('description')
        )
        created_groups[group_slug] = group.id
    return created_groups


def create_sites(site_data_list: List[Dict[str, Any]], site_groups_outputs: Dict[str, Output], clab_tenant_id_output: Output):
    """
    Responsibility: Create ONLY Site resources.
    Handles dependencies on Site Groups and Tenant.
    Returns: Dict[str, Output]: Map of slug to Site ID (Output).
    """
    print("-> Creating Sites...")
    created_sites = {}
    for site_data in site_data_list:
        site_slug = site_data['slug']
        group_id_output = site_groups_outputs.get(site_data.get('group_slug'))
        
        site = netbox.Site(site_slug,
            name=site_data['name'],
            slug=site_slug,
            status=site_data.get('status', 'active'),
            tenant_id=clab_tenant_id_output, 
            group_id=group_id_output,
            description=site_data.get('description')
        )
        created_sites[site_slug] = site.id
    return created_sites


def create_locations(location_data_list: List[Dict[str, Any]], created_sites_outputs: Dict[str, Output]):
    """
    Responsibility: Create ONLY Location resources.
    Handles dependency on Site.
    Returns: Dict[str, netbox.Location]: Map of slug to Location resource object.
    """
    print("-> Creating Locations...")
    created_locations = {}
    for location_data in location_data_list:
        location_slug = location_data['slug']
        site_slug_ref = location_data.get('site_slug')
        site_id_output = created_sites_outputs.get(site_slug_ref)

        location = netbox.Location(location_slug,
            name=location_data['name'],
            slug=location_slug,
            site_id=site_id_output,
            description=location_data.get('description')
        )
        created_locations[location_slug] = location
    return created_locations