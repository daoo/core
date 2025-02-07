"""Tests for the AVM Fritz!Box integration."""
from __future__ import annotations

from aiohttp import ClientSession

from homeassistant.components.diagnostics import REDACTED
from homeassistant.components.fritz.common import AvmWrapper
from homeassistant.components.fritz.const import DOMAIN
from homeassistant.components.fritz.diagnostics import TO_REDACT
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from .const import MOCK_USER_DATA

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry


async def test_entry_diagnostics(
    hass: HomeAssistant, hass_client: ClientSession, fc_class_mock, fh_class_mock
):
    """Test config entry diagnostics."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_USER_DATA)
    entry.add_to_hass(hass)

    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert entry.state == ConfigEntryState.LOADED

    entry_dict = entry.as_dict()
    for key in TO_REDACT:
        entry_dict["data"][key] = REDACTED
    result = await get_diagnostics_for_config_entry(hass, hass_client, entry)
    avm_wrapper: AvmWrapper = hass.data[DOMAIN][entry.entry_id]
    assert result == {
        "entry": entry_dict,
        "device_info": {
            "client_devices": [
                {
                    "connected_to": device.connected_to,
                    "connection_type": device.connection_type,
                    "hostname": device.hostname,
                    "is_connected": device.is_connected,
                    "last_activity": device.last_activity.isoformat(),
                    "wan_access": device.wan_access,
                }
                for _, device in avm_wrapper.devices.items()
            ],
            "connection_type": "WANPPPConnection",
            "current_firmware": "256.07.29",
            "discovered_services": [
                "DeviceInfo1",
                "Hosts1",
                "LANEthernetInterfaceConfig1",
                "Layer3Forwarding1",
                "UserInterface1",
                "WANCommonIFC1",
                "WANCommonInterfaceConfig1",
                "WANDSLInterfaceConfig1",
                "WANIPConn1",
                "WANPPPConnection1",
                "X_AVM-DE_Homeauto1",
                "X_AVM-DE_HostFilter1",
            ],
            "is_router": True,
            "last_exception": None,
            "last_update success": True,
            "latest_firmware": None,
            "mesh_role": "master",
            "model": "FRITZ!Box 7530 AX",
            "update_available": False,
            "wan_link_properties": {
                "NewLayer1DownstreamMaxBitRate": 318557000,
                "NewLayer1UpstreamMaxBitRate": 51805000,
                "NewPhysicalLinkStatus": "Up",
                "NewWANAccessType": "DSL",
            },
        },
    }
