# infra/atomic/ipam.py

import pulumi_netbox as netbox
from typing import Dict, Any

# --- Atomic RIRs and ASNs ---


def _create_single_rir(rir_data: Dict[str, Any]) -> netbox.Rir:
    """Creates ONLY a single RIR resource (Atomic SRP)."""
    rir_slug = rir_data['slug']
    return netbox.Rir(rir_slug,
                      name=rir_data['name'],
                      slug=rir_slug,
                      is_private=rir_data.get('is_private', False),
                      description=rir_data.get('description')
                      )


def _create_single_asn(
        asn_data: Dict[str, Any],
        rir_resources: Dict[str, netbox.Rir]
        ) -> netbox.Asn:
    """Creates ONLY a single Asn resource. Handles RIR dependency."""
    asn = asn_data['asn']
    asn_slug = f"asn-{asn}"

    rir_resource = rir_resources.get(asn_data.get('rir_slug'))

    # Fix: Cast RIR ID to integer output for NetBox API stability
    rir_id_input = rir_resource.id.apply(lambda id: int(id))

    return netbox.Asn(asn_slug,
                      asn=asn,
                      rir_id=rir_id_input,
                      description=asn_data.get('description')
                      )

# --- Atomic VRFs ---


def _create_single_vrf(vrf_data: Dict[str, Any]) -> netbox.Vrf:
    """Creates ONLY a single VRF resource (Atomic SRP)."""
    vrf_slug = vrf_data['slug']
    return netbox.Vrf(vrf_slug,
                      name=vrf_data['name'],
                      rd=vrf_data.get('rd'),
                      description=vrf_data.get('description')
                      )

# --- Atomic Prefixes and Aggregates ---


def _create_single_aggregate(
        agg_data: Dict[str, Any],
        rir_resources: Dict[str, netbox.Rir]
        ) -> netbox.Aggregate:
    """Creates ONLY a single Aggregate resource. Handles RIR dependency."""
    agg_name = agg_data['prefix'].replace('/', '_').replace('.', '_')

    rir_resource = rir_resources.get(agg_data.get('rir_slug'))

    # Fix: Cast RIR ID to integer output for NetBox API stability
    rir_id_input = rir_resource.id.apply(lambda id: int(id))

    return netbox.Aggregate(agg_name,
                            prefix=agg_data['prefix'],
                            rir_id=rir_id_input,
                            description=agg_data.get('description')
                            )


def _create_single_prefix(
        prefix_data: Dict[str, Any],
        vrf_resources: Dict[str, netbox.Vrf]
        ) -> netbox.Prefix:
    """Creates ONLY a single Prefix resource. Handles VRF dependency."""
    prefix_value = prefix_data['prefix']
    prefix_name = prefix_value.replace('/', '_').replace('.', '_')

    vrf_resource = vrf_resources.get(prefix_data.get('vrf_slug'))

    # VRF is optional
    if vrf_resource:
        # Fix: Cast VRF ID to integer output for NetBox API stability
        vrf_id_input = vrf_resource.id.apply(lambda id: int(id))
    else:
        vrf_id_input = None

    return netbox.Prefix(prefix_name,
                         prefix=prefix_value,
                         status=prefix_data.get('status', 'container'),
                         vrf_id=vrf_id_input,
                         description=prefix_data.get('description')
                         )
