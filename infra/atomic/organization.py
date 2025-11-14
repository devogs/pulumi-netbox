# infra/atomic/organization.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any

# --- Atomic Tenant Groups and Tenants ---

def _create_single_tenant_group(group_data: Dict[str, Any]) -> netbox.TenantGroup:
    """Creates ONLY a single TenantGroup resource (Atomic SRP)."""
    group_slug = group_data['slug']
    return netbox.TenantGroup(group_slug,
        name=group_data['name'],
        slug=group_slug,
        description=group_data.get('description')
    )


def _create_single_tenant(tenant_data: Dict[str, Any], created_groups_resources: Dict[str, netbox.TenantGroup]) -> netbox.Tenant:
    """Creates ONLY a single Tenant resource. Handles dependency on Tenant Groups."""
    tenant_slug = tenant_data['slug']
    group_slug_ref = tenant_data.get('group_slug')
    
    group_resource = created_groups_resources.get(group_slug_ref)
    
    group_id_input = group_resource.id.apply(lambda id: int(id)) if group_resource else None

    return netbox.Tenant(tenant_slug,
        name=tenant_data['name'],
        slug=tenant_slug,
        description=tenant_data.get('description'),
        group_id=group_id_input 
    )

# --- Atomic Sites & Locations ---

def _create_single_region(region_data: Dict[str, Any]) -> netbox.Region:
    """Creates ONLY a single Region resource (Atomic SRP)."""
    region_slug = region_data['slug']
    return netbox.Region(region_slug,
        name=region_data['name'],
        slug=region_slug,
        description=region_data.get('description')
    )


def _create_single_site_group(group_data: Dict[str, Any]) -> netbox.SiteGroup:
    """Creates ONLY a single SiteGroup resource (Atomic SRP)."""
    group_slug = group_data['slug']
    return netbox.SiteGroup(group_slug,
        name=group_data['name'],
        slug=group_slug,
        description=group_data.get('description')
    )


def _create_single_site(site_data: Dict[str, Any], site_group_resources: Dict[str, netbox.SiteGroup], clab_tenant_id_output: Output) -> netbox.Site:
    """Creates ONLY a single Site resource. Handles dependencies on Site Group and Tenant."""
    site_slug = site_data['slug']
    site_group_resource = site_group_resources.get(site_data.get('group_slug'))
    
    group_id_input = site_group_resource.id.apply(lambda id: int(id)) if site_group_resource else None
    
    return netbox.Site(site_slug,
        name=site_data['name'],
        slug=site_slug,
        status=site_data.get('status', 'active'),
        tenant_id=clab_tenant_id_output, 
        group_id=group_id_input,
        description=site_data.get('description')
    )


def _create_single_location(location_data: Dict[str, Any], site_resources: Dict[str, netbox.Site]) -> netbox.Location:
    """Creates ONLY a single Location resource. Handles dependency on Site."""
    location_slug = location_data['slug']
    site_slug_ref = location_data.get('site_slug')
    
    site_resource = site_resources.get(site_slug_ref)
    site_id_input = site_resource.id.apply(lambda id: int(id)) if site_resource else None

    return netbox.Location(location_slug,
        name=location_data['name'],
        slug=location_slug,
        site_id=site_id_input,
        description=location_data.get('description')
    )