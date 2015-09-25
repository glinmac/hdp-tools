Azure
=====

VPN / Gateway
-------------

* [Configure a VPN gateway in the Azure portal](https://azure.microsoft.com/en-gb/documentation/articles/vpn-gateway-site-to-site-create)
* [Create a virtual network with a site-to-site VPN connection using the Azure portal](https://azure.microsoft.com/en-gb/documentation/articles/vpn-gateway-configure-vpn-gateway-mp)
* [VNet-to-VNet: Connecting Virtual Networks in Azure across Different Regions](https://azure.microsoft.com/en-us/blog/vnet-to-vnet-connecting-virtual-networks-in-azure-across-different-regions)
* [Set Virtual Network Gateway Shared Key - API](https://msdn.microsoft.com/en-us/library/azure/dn770199.aspx)

API
---

    wget \
	    --debug \
	    --certificate=./cert.pem \
	    --private-key=key.pem  \
	    --header='x-ms-version: 2015-04-01' \
	    https://management.core.windows.net/<SUBSCRIPTION_ID>/services/...
