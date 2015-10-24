import logging
import datetime
import time
import netaddr

from ryu.base import app_manager
from ryu.lib import hub
from ryu.controller import handler
from ryu.services.protocols.vrrp import api as vrrp_api
from ryu.services.protocols.vrrp import event as vrrp_event


_VRRP_VERSION_V3 = 3
_VRID = 1
_VIRTUAL_IP_ADDRESS = '192.168.0.1'
_PRIMARY_IP_ADDRESS = '192.168.0.2'
_VIRTUAL_MAC_ADDRESS = '00:00:5e:00:01:01'
_PRIORITY = 250
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
        time.sleep(30)

        LOG.info("")
        LOG.info("////// 2. Change Priority [250] -> [50]  //////")
        self._configure_vrrp_change(_VRID, 50)
        time.sleep(30)

        LOG.info("")
        LOG.info("////// 3. Change Priority [50] -> [250]  //////")
        self._configure_vrrp_change(_VRID, _PRIORITY)
        time.sleep(30)

        LOG.info("")
        LOG.info("////// 4. Shutdown Vrrp Router  //////")
        self._shutdown_vrrp_router(_VRID)

    def _configure_vrrp_change(self, vrid, priority):
        instance_name = self._lookup_instance(vrid)
        if not instance_name:
            raise RPCError('vrid %d is not found' % (vrid))
        vrrp_api.vrrp_config_change(self, instance_name, priority=priority)

    def _shutdown_vrrp_router(self, vrid):
        instance_name = self._lookup_instance(vrid)
        if not instance_name:
            raise RPCError('vrid %d is not found' % (vrid))
        vrrp_api.vrrp_shutdown(self, instance_name)

    def _lookup_instance(self, vrid):
        for instance in vrrp_api.vrrp_list(self).instance_list:
            if vrid == instance.config.vrid:
                return instance.instance_name
        return None

    def _configure_vrrp_router(self, vrrp_version, vrrp_priority,
                               primary_ip_address, virtual_ip_address,
                               ifname, vrid, preempt_delay):
        interface = vrrp_event.VRRPInterfaceNetworkDevice(
            _VIRTUAL_MAC_ADDRESS, primary_ip_address, None, ifname)

        ip_addresses = [virtual_ip_address]
        config = vrrp_event.VRRPConfig(
            version=vrrp_version, vrid=vrid, priority=vrrp_priority,
            ip_addresses=ip_addresses, preempt_delay=preempt_delay)
        config_result = vrrp_api.vrrp_config(self, interface, config)
        return config_result


    @handler.set_ev_cls(vrrp_event.EventVRRPStateChanged)
    def vrrp_state_changed_handler(self, ev):
        old_state = ev.old_state
        new_state = ev.new_state
        now = datetime.datetime.now()
        now_time = now.strftime("%H:%M:%S")
        micro_time = "%03d" % (now.microsecond // 1000)
        LOG.debug("%s.%s: State Changed [%s] -> [%s]"
                 % (now_time, micro_time, old_state, new_state))
