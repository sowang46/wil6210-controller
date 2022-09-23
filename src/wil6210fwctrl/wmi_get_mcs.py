from wmi_basic import *

class WmiGetMCS(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### WMI_GET_SELECTED_RF_SECTOR_INDEX_CMDID
    WMI_CMDID = 0x863
    WMI_EVENTID = 0x1863
    cmd_args = [('cid', 1),
        ('interval_usec', 4),
    ]
    event_args = [('status', 4),
    ('tsf', 8),
    ('rssi', 1),
    ('reserved0', 3),
    ('tx_tpt', 4),
    ('tx_goodput', 4),
    ('rx_goodput', 4),
    ('bf_mcs', 2),
    ('my_rx_sector', 2),
    ('my_tx_sector', 2),
    ('other_rx_sector', 2),
    ('other_tx_sector', 2),
    ('range', 2),
    ('sqi', 1),
    ('reserved', 3),
    ]

    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['cid'] = 0
        cmd['interval_usec'] = 0 # wmi_rf_sector_type
        return cmd

    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
        cmd_data = fw.wmi_encode_cmd(cmd, self.cmd_args)
        WMI_EVENT_DATA = fw.wmi_call(self.WMI_CMDID,
                                     cmd_data,
                                     self.WMI_EVENTID, 3)

        # print WMI_EVENT_DATA
        wmi_evt = fw.wmi_decode_event(self.event_args, WMI_EVENT_DATA)
        print wmi_evt
        return wmi_evt
