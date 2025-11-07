import pulumi
import pulumi_netbox as netbox

# L'URL du serveur et l'API Token sont automatiquement utilisés 
# grâce aux configurations que vous avez définies.

# Créer un nouveau fabricant dans NetBox
test_manufacturer = netbox.Manufacturer("my-test-manufacturer",
    name="Acme-Hardware-Inc",
)

# Exporter le nom et l'ID du fabricant créé (visible après 'pulumi up')
pulumi.export("manufacturer_name", test_manufacturer.name)
pulumi.export("manufacturer_id", test_manufacturer.id)