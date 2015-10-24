import logging
import datetime

from ryu.base import app_manager
from ryu.lib import hub
from ryu.controller import handler
from ryu.services.protocols.vrrp import api as vrrp_api
from ryu.services.protocols.vrrp import event as vrrp_event


_VRRP_VERSION_V3 = 3
_VRID = 1
_VIRTUAL_IP_ADDRESS = '192.168.0.1'
_PRIMARY_IP_ADDRESS = '192.168.0.3'
_VIRTUAL_MAC_ADDRESS = '00:00:5e:00:01:01'
_PRIORITY = 100
_IFNAME = 'eth1'
_PREEMPT_DELAY = 10

LOG = logging.getLogger('SampleVrrp')
LOG.setLevel(logging.DEBUG)
logging.basicConfig()

class SampleVrrp(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SampleVrrp, self).__init__(*args, **kwargs)
        hub.spawn(self._test_senario)

    def _test_senario(self):
        LOG.info("")
        LOG.info("////// 1. Create Vrrp Router  //////")
        vrrp_mgr = self._configure_vrrp_router(_VRRP_VERSION_V3, _PRIORITY,
                      _PRIMARY_IP_ADDRESS, _VIRTUAL_IP_ADDRESS, _IFNAME,
                      _VRID, _PREEMPT_DELAY)


    def _configure_vrrp_router(self, vrrp_version, vrrp_priority,
                               primary_ip_address, virtual_ip_address,
                               ifname, vrid, preempt_delay):
        interface = vrrp_event.VRRPInterfaceNetworkDevice(
            _VIRTUAL_MAC_ADDRESS, primary_ip_address, None, ifname)

        ip_addresses = [virtual_ip_address]
        config = vrrp_event.VRRPConfig(
            version=vrrp_version, vrid=vrid, priority=vrrp_priority,
            ip_addresses=ip_addresses, preempt_delay=preempt_delay)
        rep = vrrp_api.vrrp_config(self, interface, config)
        return rep


    @handler.set_ev_cls(vrrp_event.EventVRRPStateChanged)
    def vrrp_state_changed_handler(self, ev):
        old_state = ev.old_state
        new_state = ev.new_state
        now = datetime.datetime.now()
        now_time = now.strftime("%H:%M:%S")
        micro_time = "%03d" % (now.microsecond // 1000)
        LOG.debug("%s.%s: State Changed [%s] -> [%s]"
                 % (now_time, micro_time, old_state, new_state))
