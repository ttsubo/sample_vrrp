import logging

from ryu.base import app_manager
from ryu.lib import hub
from ryu.lib import mac as lib_mac
from ryu.services.protocols.vrrp import api as vrrp_api
from ryu.services.protocols.vrrp import event as vrrp_event
#from ryu.services.protocols.vrrp import monitor_linux


_VRID = 2
_VIRTUAL_IP_ADDRESS = '192.168.3.1'
_PRIMARY_IP_ADDRESS = '192.168.3.2'
_PRIORITY = 250
_IFNAME = 'eth1'
_VRRP_VERSION_V3 = 3

LOG = logging.getLogger('SampleVrrp')
LOG.setLevel(logging.DEBUG)
logging.basicConfig()

class SampleVrrp(app_manager.RyuApp):


    def __init__(self, *args, **kwargs):
        super(SampleVrrp, self).__init__(*args, **kwargs)

    def start(self):
        hub.spawn(self._vrrp_mgr)


    def _configure_vrrp_router(self, vrrp_version, vrrp_priority,
                               primary_ip_address, virtual_ip_address,
                               ifname, vrid):
        interface = vrrp_event.VRRPInterfaceNetworkDevice(
            lib_mac.DONTCARE_STR, primary_ip_address, None, ifname)

        ip_addresses = [virtual_ip_address]
        config = vrrp_event.VRRPConfig(
            version=vrrp_version, vrid=vrid, priority=vrrp_priority,
            ip_addresses=ip_addresses)
        rep = vrrp_api.vrrp_config(self, interface, config)

        return rep

    def _vrrp_mgr(self):
        LOG.debug("////// vrrp infomation //////")
        LOG.debug("priority %s" % _PRIORITY)
        LOG.debug("primary_ip_address %s" % _PRIMARY_IP_ADDRESS)
        LOG.debug("virtual_ip_address %s" % _VIRTUAL_IP_ADDRESS)
        LOG.debug("vrid %s" % _VRID)
        LOG.debug("/////////////////////////////\n")
        vrrp_mgr = self._configure_vrrp_router(_VRRP_VERSION_V3, _PRIORITY,
                                               _PRIMARY_IP_ADDRESS,
                                               _VIRTUAL_IP_ADDRESS,
                                               _IFNAME, _VRID)

