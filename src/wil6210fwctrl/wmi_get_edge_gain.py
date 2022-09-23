from wmi_basic import *

class WmiGetEdgeGain(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### get edge gain iref table entry
    WMI_CMDID = 0x0900
    WMI_EVENTID = 0x1900
    cmd_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('device_id', 4),
        ('is_tx', 1),
        ('entry_idx', 4),
        ('use_active_idx', 1)
    ]
    event_args = [('module_id', 2),
        ('ut_subtype_id', 2),
        ('res', 4),
        ('rc_1', 4),
        ('rc_2', 4),
        ('rc_3', 4),
        ('mm_1', 4),
        ('mm_2', 4),
        ('mm_3', 4)
    ]

    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['module_id'] = 0xc
        cmd['ut_subtype_id'] = 0x51f
        cmd['device_id'] = 0
        cmd['is_tx'] = 1
        cmd['entry_idx'] = 1
        cmd['use_active_idx'] = 1
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