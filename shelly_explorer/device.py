from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .history import get_records
from .rpc import ShellyRPCClient


@dataclass(slots=True)
class ShellyDevice:
    host: str
    timeout: float = 5.0

    def client(self) -> ShellyRPCClient:
        return ShellyRPCClient(self.host, timeout=self.timeout)

    def info(self) -> dict[str, Any]:
        return self.client().get_device_info()

    def status(self) -> dict[str, Any]:
        return self.client().get_status()

    def em_status(self, em_id: int = 0) -> dict[str, Any]:
        return self.client().call('EM1.GetStatus', id=em_id)

    def em_data_status(self, em_id: int = 0) -> dict[str, Any]:
        return self.client().call('EM1Data.GetStatus', id=em_id)

    def history_records(self, em_id: int = 0) -> list[dict[str, Any]]:
        return get_records(self.client(), em_id=em_id)

    def summary(self) -> dict[str, Any]:
        info = self.info()
        status = self.status()
        em = status.get('em1:0', {})
        emdata = status.get('em1data:0', {})
        sys = status.get('sys', {})
        wifi = status.get('wifi', {})
        cloud = status.get('cloud', {})
        mqtt = status.get('mqtt', {})
        zigbee = status.get('zigbee', {})
        matter = status.get('matter', {})
        return {
            'model': info.get('model'),
            'firmware': info.get('ver'),
            'app': info.get('app'),
            'id': info.get('id'),
            'ip': wifi.get('sta_ip'),
            'wifi_rssi': wifi.get('rssi'),
            'cloud_connected': cloud.get('connected'),
            'mqtt_connected': mqtt.get('connected'),
            'zigbee_state': zigbee.get('network_state'),
            'matter_fabrics': matter.get('num_fabrics'),
            'uptime': sys.get('uptime'),
            'ram_free': sys.get('ram_free'),
            'reset_reason': sys.get('reset_reason'),
            'voltage': em.get('voltage'),
            'current': em.get('current'),
            'power': em.get('act_power'),
            'frequency': em.get('freq'),
            'total_energy': emdata.get('total_act_energy'),
            'returned_energy': emdata.get('total_act_ret_energy'),
        }
