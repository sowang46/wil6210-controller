import struct
import binascii
import subprocess
import re
import os
from wil6210_mbc_platform import *
import struct

class Wil6210MailBox:
    
    priv_data = {}

    def __init__(self):
        if os.getuid() != 0:
            print 'Please run this program as root!'
            exit()
        
        process = subprocess.Popen(['find', '/sys/bus/pci/drivers/wil6210/', '-name', '00*'], stdout=subprocess.PIPE)
        (pcie_path, _) = process.communicate()
        pcie_path = pcie_path.rstrip().splitlines()
        pcie_path_num = len(pcie_path)
        count = 1
        select = 1
        if not pcie_path_num:
            print 'wil6210 60 GHz wireless card is not found!'
            exit()

        mac_addr_all = []
        for pp in pcie_path:
            process = subprocess.Popen(['find', '%s/ieee80211' % pp, '-name', 'macaddress'], stdout=subprocess.PIPE)
            (mac_addr, _) = process.communicate()
            mac_addr_all.append(mac_addr.rstrip())
            
        if pcie_path_num > 1:
            while True:
                print '%d wil6210 60 GHz wireless cards are found! Which one (MAC address) to use?' % pcie_path_num
                for mac_addr in mac_addr_all:
                    with open(mac_addr, 'r') as f:
                        addr = f.read()
                        print '[%d] %s' % (count, addr)
                        count += 1
                print 'Enter your choice: ',
                select = int(raw_input())
                if select >= 1 and select <= pcie_path_num:
                    break
                else:
                    print 'Invalid input (%d)' % select
                    count = 1
        self.__pcie_path = pcie_path[select-1] + '/resource0'
        mac_addr_file_select = mac_addr_all[select-1]
        
        debugfs = mac_addr_file_select.replace(pcie_path[select-1], '/sys/kernel/debug').replace('macaddress', '')
        process = subprocess.Popen(['find', str(debugfs), '-name', 'wil6210'], stdout=subprocess.PIPE)
        (driver_path, _) = process.communicate()
        self.__driver_path = driver_path.rstrip()
        if not self.__driver_path:
            print 'wil6210 debugfs is not found!'
            exit()

        print 'Driver debugfs:', self.__driver_path
        print 'PCIe device:', self.__pcie_path
        
    def open(self):
        off_virt = wil6210_mbc.open_wmi_dev(self.__pcie_path)
        self.__off_virt = off_virt
        
        output_file = open(self.__driver_path + '/chip_revision','r')
        self.__chip_version = output_file.read()
        self.__chip_version = self.__chip_version.rstrip()
        output_file.close()
        chip_ver = self.get_chip_ver()
        print 'Device hardware version:', chip_ver[0], '(%s)' % chip_ver[1]
        
        output_file = open(self.__driver_path + '/fw_version','r')
        self.__fw_version = output_file.read()
        self.__fw_version = self.__fw_version.rstrip()
        output_file.close()
        print 'Device firmware version:', self.__fw_version
        
        print self.get_fw_patch()
        
    def close(self):
        wil6210_mbc.close_wmi_dev(self.__off_virt)
        
    def get_chip_ver(self):
        chip_version = {'0':'Sparrow', '3':'Sparrow_plus'}
        if self.__chip_version in chip_version.keys():
            return self.__chip_version, chip_version[self.__chip_version]
        else:
            return self.__chip_version, 'Unknown'
        
    def get_fw_ver(self):
        return self.__fw_version
        
    def get_off_virt(self):
        return self.__off_virt
        
    def get_fw_patch(self):
        try:
            msg_data = self.mem_dump(0x93FF00, 0x80)
            msg_data_len = len(msg_data)
            msg_all = struct.unpack('%ds' % msg_data_len, msg_data)[0]
            msg = ''
            for m in msg_all:
                if m != '\n':
                    msg += m
            if msg[0:7] == 'Patched':
                msg = msg.rstrip(msg[-1])[:-2]
                return 'Firmware patched'+msg[7:]
            else:
                return 'Firmware patched: none'
        except Exception as e:
            print e
            pass
        return ""
        
    def __mbc_read_wmi__(self, WMI_EVTID, TRY_NUM, TIME_GAP):
        ret = wil6210_mbc.read_wmi(WMI_EVTID, TRY_NUM, TIME_GAP, self.__off_virt)
        if ret is not None:
            return binascii.hexlify(ret)
        
    def mem_read(self, addr, size):
        return wil6210_mbc.mem_read(addr, size, self.__off_virt)
        
    def mem_write(self, addr, val):
        return wil6210_mbc.mem_write(val, addr, self.__off_virt)
        
    def mem_block_write(self, addr, data_list):
        mem_block_write_args = [('instr', 0),
            ('addr', 4),
            ('size', 4),
            ('raw_data', 0),
        ]
        
        mem_block_write_params = {}
        mem_block_write_params['instr'] = self.__off_virt
        mem_block_write_params['addr'] = addr
        mem_block_write_params['size'] = len(data_list)
        mem_block_write_params['raw_data'] = struct.pack("%dI" % len(data_list), *data_list)

        mem_block_write_data = self.wmi_encode_cmd(mem_block_write_params, 
                                                   mem_block_write_args)
        
        return wil6210_mbc.mem_block_write(mem_block_write_data)
        
    def mem_dump(self, addr, size):
        return wil6210_mbc.mem_dump(addr, size, self.__off_virt)
        
    def usleep(self, time_in_us):
        try:
            wil6210_mbc.us_sleep(time_in_us)
        except Exception as e:
            print e
        
    def __send_wmi__(self, wmi_cmd_hdr):
        output_file = open(self.__driver_path + '/wmi_send','wb')
        output_file.write(wmi_cmd_hdr)
        # print 'Send: %s' % binascii.hexlify(wmi_cmd_hdr)
        output_file.close()
        
    def send_wmi(self, WMI_CMDID, WMI_CONTENT):
        wmi_cmd_hdr_mid = 0
        wmi_cmd_hdr_reserved = 0
        wmi_cmd_hdr_command_id = WMI_CMDID
        wmi_cmd_hdr_fw_timestamp = 0
        wmi_cmd_hdr = struct.pack('BBHI', wmi_cmd_hdr_mid, 
                                  wmi_cmd_hdr_reserved, 
                                  wmi_cmd_hdr_command_id, 
                                  wmi_cmd_hdr_fw_timestamp)
        self.__send_wmi__(wmi_cmd_hdr+WMI_CONTENT)
        print 'CMD: 0x%04x %s' % (WMI_CMDID, binascii.hexlify(WMI_CONTENT))
    
    # deprecated
    def __read_wmi__deprecated(self, WMI_EVTID):
        output_file = open(self.__driver_path + '/mbox','r')
        mbox = output_file.read()
        rx_ring_start_idx = mbox.find('entry size = 1296')
        rx_ring_content = mbox[rx_ring_start_idx:]
        
        rx_ring_data = re.findall('([\w ]{2})\] . [ ]+(0x\w+) -> ([\w\ ]+)\n([\w\ :\n\}]+)', rx_ring_content, re.I);
        
        data = []
        for d in rx_ring_data:
            if len(d[3]) > 5:
                data_bytes = re.findall('\ ([\da-f]{2})', d[3], re.I)
                data.append(''.join(data_bytes))
        
        for data_entry in data:
            wmi_evt_hdr_data = data_entry[0:16]
            wmi_evt_hdr = struct.unpack('BBHI', binascii.unhexlify(wmi_evt_hdr_data));
            print '============='
            print '0x%04x' % wmi_evt_hdr[2]
            print '0x%04x' % int(WMI_EVTID)
            print '============='
            if wmi_evt_hdr[2] != int(WMI_EVTID):
                continue
                
            wmi_evt_content_data = data_entry[16:]
            return wmi_evt_content_data
    
    # deprecated
    def read_wmi_deprecated(self, WMI_EVTID, TIME_OUT):
        ret = self.__read_wmi__deprecated(WMI_EVTID)
        while ret is None and TIME_OUT:
            ret = self.__read_wmi__deprecated(WMI_EVTID)
            TIME_OUT -= 1
        if ret is None and not TIME_OUT:
            print "Event: 0x%04x time out" % WMI_EVTID
        return ret
    
    def read_wmi(self, WMI_EVTID, TIME_OUT, TIME_GAP=10):
        return self.__mbc_read_wmi__(WMI_EVTID, TIME_OUT, TIME_GAP)

    def wmi_call(self, WMI_CMDID, WMI_CONTENT, WMI_EVTID, TIME_OUT, TIME_GAP=10):
        self.send_wmi(WMI_CMDID, WMI_CONTENT)
        return self.read_wmi(WMI_EVTID, TIME_OUT, TIME_GAP)
    
    def wmi_decode_event(self, event_args, WMI_EVENT_DATA):
        if WMI_EVENT_DATA is None:
            return
        WMI_EVENT_DATA = binascii.unhexlify(WMI_EVENT_DATA)
        idx = 0
        wmi_evt = {}
        for arg in event_args:
            if (arg[1] == 0):
                val = [binascii.hexlify(WMI_EVENT_DATA[idx:])]
            elif (arg[1] == 1):
                val = struct.unpack('B', WMI_EVENT_DATA[idx:idx+1])
            elif (arg[1] == 2):
                val = struct.unpack('H', WMI_EVENT_DATA[idx:idx+2])
            elif (arg[1] == 4):
                val = struct.unpack('I', WMI_EVENT_DATA[idx:idx+4])
            elif (arg[1] == 8):
                val = struct.unpack('Q', WMI_EVENT_DATA[idx:idx+8])
            else:
                val = [binascii.hexlify(WMI_EVENT_DATA[idx:idx+arg[1]])]
            
            idx += arg[1]
            wmi_evt[arg[0]] = val[0]
            if (arg[1] == 0):
                break
            
        return wmi_evt
        
    def wmi_encode_cmd(self, cmd_content, cmd_args):
        WMI_CMD_CONTENT = b''
        for arg in cmd_args:
            if (arg[1] == 0):
                WMI_CMD_CONTENT += cmd_content[arg[0]]
            elif (arg[1] == 1):
                WMI_CMD_CONTENT += struct.pack('B', cmd_content[arg[0]])
            elif (arg[1] == 2):
                WMI_CMD_CONTENT += struct.pack('H', cmd_content[arg[0]])
            elif (arg[1] == 4):
                WMI_CMD_CONTENT += struct.pack('I', cmd_content[arg[0]])
            elif (arg[1] == 8):
                WMI_CMD_CONTENT += struct.pack('Q', cmd_content[arg[0]])
            else:
                WMI_CMD_CONTENT += binascii.unhexlify(cmd_content[arg[0]])
        return WMI_CMD_CONTENT
        
    def reverse_endian(self, hex_str):
        return hex_str[6:8] + hex_str[4:6] + hex_str[2:4] + hex_str[0:2]

    def caller(self, target, cmd=None, times=1, delay_in_us=20000):
        while True:
            resp = target.call(self, cmd)
            times -= 1
            if times == 0:
                return resp
            self.usleep(delay_in_us)
        return resp

    def get_fw_params(self, params):
        if self.__fw_version in params.keys():
            return params[self.__fw_version]
        else:
            raise Exception("Cannot find params", params, "for fw_version:", self.__fw_version)