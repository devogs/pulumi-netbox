# infra/ipam.py

import pulumi_netbox as netbox
from pulumi import Output
from typing import Dict, List, Any

# --- RIRs and ASNs ---

def create_rirs(rir_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Rir]:
    """Responsibility: Create ONLY RIR resources."""
    print("-> Creating RIRs...")
    created_rirs = {}
    for rir_data in rir_data_list:
        rir_slug = rir_data['slug']
        rir = netbox.Rir(rir_slug,
            name=rir_data['name'],
            slug=rir_slug,
            is_private=rir_data.get('is_private', False),
            description=rir_data.get('description')
        )
        # Returns the full resource object
        created_rirs[rir_slug] = rir
    return created_rirs


def create_asns(asn_data_list: List[Dict[str, Any]], rir_resources: Dict[str, netbox.Rir]) -> Dict[int, netbox.Asn]:
    """Responsibility: Create ONLY Asn resources. Handles dependency on RIRs."""
    print("-> Creating ASNs...")
    created_asns = {}
    for asn_data in asn_data_list:
        asn = asn_data['asn']
        asn_slug = f"asn-{asn}"
        
        rir_resource = rir_resources.get(asn_data.get('rir_slug'))

        # Fix: Cast RIR ID to integer output for NetBox API stability
        asn_resource = netbox.Asn(asn_slug,
            asn=asn,
            rir_id=rir_resource.id.apply(lambda id: int(id)),
            description=asn_data.get('description')
        )
        created_asns[asn] = asn_resource
    return created_asns

# --- VRFs ---

def create_vrfs(vrf_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Vrf]:
    """Responsibility: Create ONLY VRF resources."""
    print("-> Creating VRFs...")
    created_vrfs = {}
    for vrf_data in vrf_data_list:
        vrf_slug = vrf_data['slug']
        vrf = netbox.Vrf(vrf_slug,
            name=vrf_data['name'],
            rd=vrf_data.get('rd'), # Route Distinguisher (optional)
            description=vrf_data.get('description')
        )
        # Returns the full resource object (corrected from returning .id)
        created_vrfs[vrf_slug] = vrf
    return created_vrfs

# --- Prefixes and Aggregates ---

def create_aggregates(aggregate_data_list: List[Dict[str, Any]], rir_resources: Dict[str, netbox.Rir]) -> Dict[str, netbox.Aggregate]:
    """Responsibility: Create ONLY Aggregate resources. Handles dependency on RIRs."""
    print("-> Creating Aggregates...")
    created_aggregates = {}
    for agg_data in aggregate_data_list:
        # Use the prefix as the Pulumi resource name for uniqueness
        agg_name = agg_data['prefix'].replace('/', '_').replace('.', '_')
        
        rir_resource = rir_resources.get(agg_data.get('rir_slug'))

        # Fix: Cast RIR ID to integer output for NetBox API stability
        rir_id_input = rir_resource.id.apply(lambda id: int(id))

        aggregate = netbox.Aggregate(agg_name,
            prefix=agg_data['prefix'],
            rir_id=rir_id_input,
            description=agg_data.get('description')
        )
        created_aggregates[agg_data['prefix']] = aggregate
    return created_aggregates


def create_prefixes(prefix_data_list: List[Dict[str, Any]], vrf_resources: Dict[str, netbox.Vrf]) -> Dict[str, netbox.Prefix]:
    """Responsibility: Create ONLY Prefix resources. Handles dependency on VRFs."""
    print("-> Creating Prefixes...")
    created_prefixes = {}
    for prefix_data in prefix_data_list:
        prefix_value = prefix_data['prefix']
        prefix_name = prefix_value.replace('/', '_').replace('.', '_')
        
        vrf_resource = vrf_resources.get(prefix_data.get('vrf_slug'))
        
        # VRF is optional (can be None if the prefix is 'global')
        if vrf_resource:
            # Fix: Cast VRF ID to integer output for NetBox API stability
            vrf_id_input = vrf_resource.id.apply(lambda id: int(id))
        else:
            vrf_id_input = None

        prefix = netbox.Prefix(prefix_name,
            prefix=prefix_value,
            status=prefix_data.get('status', 'container'),
            vrf_id=vrf_id_input,
            description=prefix_data.get('description')
        )
        created_prefixes[prefix_value] = prefix
    return created_prefixes