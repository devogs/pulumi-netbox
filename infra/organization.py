# infra/organization.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any


def create_tenant_groups(group_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.TenantGroup]:
    """
    Responsibility: Create ONLY TenantGroup resources.
    Returns: Dict[str, netbox.TenantGroup]: Map of slug to TenantGroup resource object.
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
        # FIX: Return the full resource object
        created_groups[group_slug] = group 
        
    return created_groups


def create_tenants(tenant_data_list: List[Dict[str, Any]], created_groups_outputs: Dict[str, netbox.TenantGroup]) -> Dict[str, netbox.Tenant]:
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
        
        # Dependency resolution using the full resource object
        group_resource = created_groups_outputs.get(group_slug_ref)
        
        # FIX: Access .id of the resource object and apply int() cast
        group_id_input = group_resource.id.apply(lambda id: int(id)) if group_resource else None

        tenant = netbox.Tenant(tenant_slug,
            name=tenant_data['name'],
            slug=tenant_slug,
            description=tenant_data.get('description'),
            group_id=group_id_input 
        )
        created_tenants[tenant_slug] = tenant
        
    return created_tenants

# --- Functions for Sites & Locations ---

def create_regions(region_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Region]:
    """
    Responsibility: Create ONLY Region resources.
    Returns: Dict[str, netbox.Region]: Map of slug to Region resource object.
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
        # FIX: Return the full resource object
        created_regions[region_slug] = region
    return created_regions


def create_site_groups(group_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.SiteGroup]:
    """
    Responsibility: Create ONLY SiteGroup resources.
    Returns: Dict[str, netbox.SiteGroup]: Map of slug to SiteGroup resource object.
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
        # FIX: Return the full resource object
        created_groups[group_slug] = group
    return created_groups


def create_sites(site_data_list: List[Dict[str, Any]], site_group_resources: Dict[str, netbox.SiteGroup], clab_tenant_id_output: Output) -> Dict[str, netbox.Site]:
    """
    Responsibility: Create ONLY Site resources.
    Handles dependencies on Site Groups and Tenant.
    Returns: Dict[str, netbox.Site]: Map of slug to Site resource object.
    """
    print("-> Creating Sites...")
    created_sites = {}
    for site_data in site_data_list:
        site_slug = site_data['slug']
        site_group_resource = site_group_resources.get(site_data.get('group_slug'))
        
        # Dependency resolution
        group_id_input = site_group_resource.id.apply(lambda id: int(id)) if site_group_resource else None
        
        site = netbox.Site(site_slug,
            name=site_data['name'],
            slug=site_slug,
            status=site_data.get('status', 'active'),
            tenant_id=clab_tenant_id_output, 
            group_id=group_id_input,
            description=site_data.get('description')
        )
        # FIX: Return the full resource object
        created_sites[site_slug] = site
    return created_sites


def create_locations(location_data_list: List[Dict[str, Any]], site_resources: Dict[str, netbox.Site]) -> Dict[str, netbox.Location]:
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
        
        # Dependency resolution
        site_resource = site_resources.get(site_slug_ref)
        site_id_input = site_resource.id.apply(lambda id: int(id)) if site_resource else None

        location = netbox.Location(location_slug,
            name=location_data['name'],
            slug=location_slug,
            site_id=site_id_input,
            description=location_data.get('description')
        )
        created_locations[location_slug] = location
    return created_locations