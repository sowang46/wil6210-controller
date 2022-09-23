from wil6210_mb import *
import importlib

MODULE_LIST = [
    # MODULE_NAME, COMMAND_NAME, CLASS_NAME
    ('wmi_aoa_meas', 'aoa_meas', 'WmiAoaMeas'),
    ('wmi_basic', 'basic', 'WmiBasic'),
    ('wmi_beacon_send', 'beacon_send', 'WmiBeaconSend'),
    ('wmi_channel_estimation', 'channel_estimate', 'WmiChEst'),
    ('wmi_echo', 'echo', 'WmiEcho'),
    ('wmi_fw_console', 'fw_console', 'WmiFwConsole'),
    ('wmi_fw_trace', 'fw_trace', 'WmiFwTrace'),
    ('wmi_fw_ver', 'fw_ver', 'WmiFwVer'),
    ('wmi_get_bb_status', 'get_bb_status', 'WmiGetBbStatus'),
    ('wmi_get_beamforming_statistics', 'get_bf_stat', 'WmiGetBfStats'),
    ('wmi_get_call_log', 'call_log', 'WmiGetCallLog'),
    ('wmi_get_cir', 'get_cir', 'WmiGetCir'),
    ('wmi_get_pattern', 'get_pattern', 'WmiGetPattern'),
    ('wmi_get_ps', 'get_ps', 'WmiGetPowerSave'),
    ('wmi_get_rf_status', 'get_rf_status', 'WmiGetRfStatus'),
    ('wmi_get_rfc_cmd_enabled', 'get_rfc_cmd_enabled', 'WmiGetRfcCmdEnable'),
    ('wmi_get_rfc_gain_index', 'get_rfc_gain', 'WmiGetRfcGain'),
    ('wmi_get_rssi', 'get_rssi', 'WmiGetRSSI'),
    ('wmi_get_rx_packet_phy', 'get_rx_pkt_phy', 'WmiGetRxPacketPhy'),
    ('wmi_get_rx_sar_rssi', 'get_rx_sar_rssi', 'WmiGetRxSarRssi'),
    ('wmi_get_sector', 'get_sector', 'WmiGetSector'),
    ('wmi_mem_dump', 'mem_dump', 'WmiMemDump'),
    ('wmi_mem_write', 'mem_write', 'WmiMemWrite'),
    ('wmi_per_beam_cir', 'per_beam_cir', 'WmiGetBeamCir'),
    ('wmi_per_beam_rss', 'per_beam_rss', 'WmiGetBeamRss'),
    ('wmi_per_beam_rss2', 'per_beam_rss2', 'WmiGetBeamRss2'),
    ('wmi_per_beam_rss3', 'per_beam_rss3', 'WmiGetBeamRss3'),
    ('wmi_per_beam_rss4', 'per_beam_rss4', 'WmiGetBeamRss4'),
    ('wmi_per_beam_rss5', 'per_beam_rss5', 'WmiGetBeamRss5'),
    ('wmi_per_beam_rss_filterap', 'per_beam_rss_filterap', 'WmiSetBeamRssApFilter'),
    ('wmi_per_beam_rss_multiap', 'per_beam_rss_multiap', 'WmiGetBeamRssMultiAp'),
    ('wmi_per_beam_snr', 'per_beam_snr', 'WmiGetBeamSnr'),
    ('wmi_per_beam_snr_128', 'per_beam_snr_128', 'WmiGetBeamSnr128'),
    ('wmi_per_frame_rss', 'per_frame_rss', 'WmiGetFrameRss'),
    ('wmi_periodic_sweep', 'periodic_sweep', 'WmiPeriodicSweep'),
    ('wmi_phy_tx', 'phy_tx', 'WmiPhyTx'),
    ('wmi_rx_mode', 'rx_mode', 'WmiRxMode'),
    ('wmi_set_codebook_active', 'set_codebook_active', 'WmiSetCodebookActive'),
    ('wmi_set_codebook_entry', 'set_codebook_entry', 'WmiSetCodebookEntry'),
    ('wmi_set_mcs', 'set_mcs', 'WmiSetMcs'),
    ('wmi_set_pattern', 'set_pattern', 'WmiSetPattern'),
    ('wmi_set_pattern2', 'set_pattern2', 'WmiSetPattern2'),
    ('wmi_set_rf_module', 'set_rf_module', 'WmiSetRfModule'),
    ('wmi_set_rfc_cmd_enabled', 'set_rfc_cmd_enabled', 'WmiSetRfcCmdEnable'),
    ('wmi_set_rfc_gain_index', 'set_rfc_gain', 'WmiSetRfcGain'),
    ('wmi_set_rx_agc_index', 'set_rx_agc', 'WmiSetRxAgc'),
    ('wmi_set_rx_agc_steps_disable', 'set_rx_agc_step_disable', 'WmiSetRxAgcStepsDisable'),
    ('wmi_set_sector', 'set_sector', 'WmiSetSector'),
    ('wmi_set_sector_number', 'set_sector_number', 'WmiSetSectorNumber'),
    ('wmi_set_tx_sectgain', 'set_tx_sector_gain', 'WmiSetTxSectGain'),
    ('wmi_set_tx_sector_order', 'set_sector_order', 'WmiSetTxSectorOrder'),
    ('wmi_tof_channel_info', 'tof_channel', 'WmiTofChannelInfo'),
    ('wmi_tof_get_capabilities', 'tof_cap', 'WmiTofGetCapabilities'),
    ('wmi_tof_session_start', 'tof_start', 'WmiTofSessionStart'),
    ('wmi_tx_mode', 'tx_mode', 'WmiTxMode'),
    ('wmi_tx_mgmt', 'tx_mgmt', 'WmiTxMgmt'),
    ('wmi_tx_sin', 'tx_sin', 'WmiTxSin'),
    ('wmi_get_ssid', 'get_ssid', 'WmiGetSSID'),
    ('wmi_get_mcs', 'get_mcs', 'WmiGetMCS'),
    ('wmi_periodic_module', 'periodic_module', 'WmiPeriodicModule'),
    ('wmi_set_codebook_block', 'set_codebook_block', 'WmiSetCodebookBlock'),
    ('wmi_get_edge_gain', 'get_edge_gain', 'WmiGetEdgeGain'),
    ('wmi_per_beam_rss_v2x', 'per_beam_rss_v2x', 'WmiBeamRssV2X'),
    ('wmi_start_scan', 'start_scan', 'WmiStartScan'),
]

PROJECT = 'wil6210fwctrl'

print '''
                 Wil6210 Firmware Controller
                  Teng Wei (twei7@wisc.edu)

                       !!! WARNING !!!
This is a proprietary software. Do not redistribute it without written 
permission from WCSN group, UCSD. The software may damage your hardware 
and may void your hardware's warranty! You use our tools at your own 
risk and responsibility.
'''

SUPPORTED_WMI = {}
NOT_LOAD = []
for module in MODULE_LIST:
    try:
        m = importlib.import_module('.'+module[0], PROJECT)
        SUPPORTED_WMI[module[1]] = getattr(m, module[2])
    except:
        NOT_LOAD.append(module[0])
        pass

print 'Loaded %d Modules:' % len(SUPPORTED_WMI.keys()),
print '/\n\t'.join(['/'.join(sorted(SUPPORTED_WMI.keys())[i:i+3]) \
                  for i in range(0, len(SUPPORTED_WMI.keys()), 3)])
print 'Not loaded %d Modules:' % len(NOT_LOAD),
print '/\n\t'.join(['/'.join(sorted(NOT_LOAD)[i:i+3]) \
                  for i in range(0, len(NOT_LOAD), 3)])
print ''
