from wmi_basic import *
from wil6210_mbc_platform import *
import binascii
import struct

class WmiSetCodebookEntry(WmiBasic):
    # List of WMI commands, events format can be found here:
    # https://git.kernel.org/pub/scm/linux/kernel/git/kvalo/ath.git/tree/drivers/net/wireless/ath/wil6210/wmi.h
    #### set codebook entry
    WMI_CMDID = 0x0
    WMI_EVENTID = 0x0
    cmd_args = [('codebook_idx', 2),
        ('sector_idx', 2),
        ('mag', 32),
        ('phase', 32),
        ('amp', 8),
        ('store_data', 2),
        ('query', 2),
    ]
    event_args = [
    ]
    
    sector_dist_args = [
        ('psh_hi_val', 4),
        ('psh_lo_val', 4),
        ('etype0_val', 4),
        ('etype1_val', 4),
        ('etype2_val', 4),
        ('dtype_swch_off_val', 4),
    ]
    
    codebook_start_addr = 0x008fcb00
    codebook_offset = 0x600+0x30
    
    fw_priv_data = 'codebook_data'
    
    @classmethod
    def cmdDefault(self):
        cmd = self.wmi_get_cmd(self.cmd_args)
        cmd['codebook_idx'] = 0
        cmd['sector_idx'] = 0
        cmd['mag'] = "00000000000000000000000000000000"
        cmd['phase'] = "00000000000000000000000000000000"
        cmd['amp'] = "00000000"
        cmd['store_data'] = 0
        cmd['query'] = 0
        return cmd
    
    @classmethod
    def call(self, fw, cmd=None):
        if cmd is None:
            cmd = self.cmdDefault()
            
        if self.fw_priv_data not in fw.priv_data.keys():
            fw.priv_data[self.fw_priv_data] = {}
            
        if cmd['query']:
            return [(k, len(d)) for k, d in fw.priv_data[self.fw_priv_data].iteritems()]
            
        if cmd['codebook_idx'] not in fw.priv_data[self.fw_priv_data].keys():
            fw.priv_data[self.fw_priv_data][cmd['codebook_idx']] = []
        
        if cmd['codebook_idx'] < 0:
            fw.priv_data[self.fw_priv_data] = {}
            return [0]
            
        sector_dist = self.wmi_get_cmd(self.sector_dist_args)
        sectors_info = wil6210_mbc.cfg_verify_convert(cmd['mag']+cmd['phase']+cmd['amp'])
        sectors_val = struct.unpack('6I', sectors_info)
        sector_dist['psh_hi_val'] = sectors_val[0]
        sector_dist['psh_lo_val'] = sectors_val[1]
        sector_dist['etype0_val'] = sectors_val[2]
        sector_dist['etype1_val'] = sectors_val[3]
        sector_dist['etype2_val'] = sectors_val[4]
        sector_dist['dtype_swch_off_val'] = sectors_val[5]
        
        if not cmd['store_data']:
            codebook_addr = self.codebook_start_addr + self.codebook_offset * cmd['codebook_idx']
            codebook_entry_addr = codebook_addr + 4*6*cmd['sector_idx']
            fw.mem_write(codebook_entry_addr+0*4, sector_dist['psh_hi_val'])
            fw.mem_write(codebook_entry_addr+1*4, sector_dist['psh_lo_val'])
            fw.mem_write(codebook_entry_addr+2*4, sector_dist['etype0_val'])
            fw.mem_write(codebook_entry_addr+3*4, sector_dist['etype1_val'])
            fw.mem_write(codebook_entry_addr+4*4, sector_dist['etype2_val'])
            fw.mem_write(codebook_entry_addr+5*4, sector_dist['dtype_swch_off_val'])
        else:
            if cmd['sector_idx'] < 0:
                fw.priv_data[self.fw_priv_data][cmd['codebook_idx']] = []
            else:
                fw.priv_data[self.fw_priv_data][cmd['codebook_idx']].append((cmd['sector_idx'], 
                    sector_dist['psh_hi_val'],
                    sector_dist['psh_lo_val'],
                    sector_dist['etype0_val'],
                    sector_dist['etype1_val'],
                    sector_dist['etype2_val'],
                    sector_dist['dtype_swch_off_val']))


        # print 'write %s, %s, %s, %s, %s, %s to 0x%02x' % (sector_dist['psh_hi_val'],
        #                                                   sector_dist['psh_lo_val'],
        #                                                   sector_dist['etype0_val'],
        #                                                   sector_dist['etype1_val'],
        #                                                   sector_dist['etype2_val'],
        #                                                   sector_dist['dtype_swch_off_val'],
        #                                                   codebook_entry_addr)

        return [0]