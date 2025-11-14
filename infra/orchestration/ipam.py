# infra/orchestration/ipam.py

import pulumi_netbox as netbox
from typing import Dict, List, Any
# Import all atomic helpers
from infra.atomic.ipam import (
    _create_single_rir, _create_single_asn, _create_single_vrf,
    _create_single_aggregate, _create_single_prefix
)


# --- Orchestration RIRs and ASNs (Preserves original function signature) ---

def create_rirs(rir_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Rir]:
    """Responsibility: Orchestrate the creation of ALL RIR resources."""
    print("-> Creating RIRs...")
    created_rirs = {}
    for rir_data in rir_data_list:
        rir = _create_single_rir(rir_data)
        created_rirs[rir_data['slug']] = rir
    return created_rirs


def create_asns(
        asn_data_list: List[Dict[str, Any]],
        rir_resources: Dict[str, netbox.Rir]
        ) -> Dict[int, netbox.Asn]:
    """Responsibility: Orchestrate the creation of ALL Asn resources."""
    print("-> Creating ASNs...")
    created_asns = {}
    for asn_data in asn_data_list:
        asn_resource = _create_single_asn(asn_data, rir_resources)
        created_asns[asn_data['asn']] = asn_resource
    return created_asns

# --- Orchestration VRFs ---


def create_vrfs(vrf_data_list: List[Dict[str, Any]]) -> Dict[str, netbox.Vrf]:
    """Responsibility: Orchestrate the creation of ALL VRF resources."""
    print("-> Creating VRFs...")
    created_vrfs = {}
    for vrf_data in vrf_data_list:
        vrf = _create_single_vrf(vrf_data)
        created_vrfs[vrf_data['slug']] = vrf
    return created_vrfs

# --- Orchestration Prefixes and Aggregates ---


def create_aggregates(
        aggregate_data_list: List[Dict[str, Any]],
        rir_resources: Dict[str, netbox.Rir]
        ) -> Dict[str, netbox.Aggregate]:
    """Responsibility: Orchestrate the creation of ALL Aggregate resources."""
    print("-> Creating Aggregates...")
    created_aggregates = {}
    for agg_data in aggregate_data_list:
        aggregate = _create_single_aggregate(agg_data, rir_resources)
        created_aggregates[agg_data['prefix']] = aggregate
    return created_aggregates


def create_prefixes(
        prefix_data_list: List[Dict[str, Any]],
        vrf_resources: Dict[str, netbox.Vrf]
        ) -> Dict[str, netbox.Prefix]:
    """Responsibility: Orchestrate the creation of ALL Prefix resources."""
    print("-> Creating Prefixes...")
    created_prefixes = {}
    for prefix_data in prefix_data_list:
        prefix = _create_single_prefix(prefix_data, vrf_resources)
        created_prefixes[prefix_data['prefix']] = prefix
    return created_prefixes
