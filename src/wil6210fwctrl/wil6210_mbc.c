#include <Python.h>
#include <stdio.h>      /* printf */
#include <stddef.h>     /* offsetof */
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

// #define MBC_DEBUG

#define likely(x)       __builtin_expect((x),1)
#define unlikely(x)     __builtin_expect((x),0)

#define max(x, y) (((x) > (y)) ? (x) : (y))
#define min(x, y) (((x) < (y)) ? (x) : (y))
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))

#define le16_to_cpus(x) do { (void)(x); } while (0)
#define le32_to_cpus(x) do { (void)(x); } while (0)
#define le16_to_cpu(val) (val)
#define le32_to_cpu(val) (val)

#define true 1
#define false 0

#define WIL6210_FW_HOST_OFF      (0x880000UL)
#define RGF_USER_USER_SCRATCH_PAD	(0x8802bc)
#define RGF_MBOX   RGF_USER_USER_SCRATCH_PAD
#define HOSTADDR(fwaddr)        (fwaddr - WIL6210_FW_HOST_OFF)
#define HOST_MBOX   HOSTADDR(RGF_MBOX)

#define MAX_MBOXITEM_SIZE   (240)

const char hex_asc[] = "0123456789abcdef";
#define hex_asc_lo(x)	hex_asc[((x) & 0x0f)]
#define hex_asc_hi(x)	hex_asc[((x) & 0xf0) >> 4]

#define PRINT_ERROR \
	do { \
		fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
		__LINE__, __FILE__, errno, strerror(errno)); exit(1); \
	} while(0)
	
typedef unsigned char bool;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long u64;
typedef unsigned char __le8;
typedef unsigned short __le16;
typedef unsigned int __le32;
typedef unsigned long __le64;
typedef int32_t s32;

enum {
	DUMP_PREFIX_NONE,
	DUMP_PREFIX_ADDRESS,
	DUMP_PREFIX_OFFSET
};

struct wil6210_mbox_ring {
	u32 base;
	u16 entry_size; /* max. size of mbox entry, incl. all headers */
	u16 size;
	u32 tail;
	u32 head;
};

struct wil6210_mbox_ring_desc {
	__le32 sync;
	__le32 addr;
};

struct wil6210_mbox_ctl {
	struct wil6210_mbox_ring tx;
	struct wil6210_mbox_ring rx;
};

struct wil6210_mbox_hdr {
	__le16 seq;
	__le16 len; /* payload, bytes after this header */
	__le16 type;
	u8 flags;
	u8 reserved;
};

struct wmi_cmd_hdr {
	u8 mid;
	u8 reserved;
	__le16 command_id;
	__le32 fw_timestamp;
};

/* Hardware definitions end */
struct fw_map {
	u32 from; /* linker address - from, inclusive */
	u32 to;   /* linker address - to, exclusive */
	u32 host; /* PCI/Host address - BAR0 + 0x880000 */
	const char *name; /* for debugfs */
	bool fw; /* true if FW mapping, false if UCODE mapping */
};

const struct fw_map fw_mapping[] = {
	/* FW code RAM 256k */
	{0x000000, 0x040000, 0x8c0000, "fw_code", true},
	/* FW data RAM 32k */
	{0x800000, 0x808000, 0x900000, "fw_data", true},
	/* periph data 128k */
	{0x840000, 0x860000, 0x908000, "fw_peri", true},
	/* various RGF 40k */
	{0x880000, 0x88a000, 0x880000, "rgf", true},
	/* AGC table   4k */
	{0x88a000, 0x88b000, 0x88a000, "AGC_tbl", true},
	/* Pcie_ext_rgf 4k */
	{0x88b000, 0x88c000, 0x88b000, "rgf_ext", true},
	/* mac_ext_rgf 512b */
	{0x88c000, 0x88c200, 0x88c000, "mac_rgf_ext", true},
	/* upper area 548k */
	{0x8c0000, 0x949000, 0x8c0000, "upper", true},
	/* UCODE areas - accessible by debugfs blobs but not by
	 * wmi_addr_remap. UCODE areas MUST be added AFTER FW areas!
	 */
	/* ucode code RAM 128k */
	{0x000000, 0x020000, 0x920000, "uc_code", false},
	/* ucode data RAM 16k */
	{0x800000, 0x804000, 0x940000, "uc_data", false},
};

/* Content of RF Sector (six 32-bits registers) */
struct wmi_rf_sector_info {
  /* Phase values for RF Chains[15-0] (2bits per RF chain) */
  __le32 psh_hi;
  /* Phase values for RF Chains[31-16] (2bits per RF chain) */
  __le32 psh_lo;
  /* ETYPE Bit0 for all RF chains[31-0] - bit0 of Edge amplifier gain
   * index
   */
  __le32 etype0;
  /* ETYPE Bit1 for all RF chains[31-0] - bit1 of Edge amplifier gain
   * index
   */
  __le32 etype1;
  /* ETYPE Bit2 for all RF chains[31-0] - bit2 of Edge amplifier gain
   * index
   */
  __le32 etype2;
  /* D-Type values (3bits each) for 8 Distribution amplifiers + X16
   * switch bits
   */
  __le32 dtype_swch_off;
} __packed;

struct module_level_enable { /* Little Endian */
	uint error_level_enable : 1;
	uint warn_level_enable : 1;
	uint info_level_enable : 1;
	uint verbose_level_enable : 1;
	uint reserved0 : 4;
} __attribute__((packed));

struct log_trace_header { /* Little Endian */
	/* the offset of the trace string in the strings sections */
	uint strring_offset : 20;
	uint module : 4; /* module that outputs the trace */
	/*	0 - Error
		1- WARN
		2 - INFO
		3 - VERBOSE */
	uint level : 2;
	uint parameters_num : 2; /* [0..3] */
	uint is_string : 1; /* indicate if the printf uses %s */
	uint signature : 3; /* should be 5 (2'101) in valid header */
} __attribute__((packed));

union log_event {
	struct log_trace_header hdr;
	u32 param;
} __attribute__((packed));

struct log_table_header {
	u32 write_ptr; /* incremented by trace producer every write */
	struct module_level_enable module_level_enable[16];
	union log_event evt[0];
} __attribute__((packed));

char *u32tobin(u32 a, char *buffer) {
    buffer[32] = '\0';
    buffer += 31;
    for (int i = 31; i >= 0; i--) {
        *buffer-- = (a & 1) + '0';
        a >>= 1;
    }
    return buffer;
}

int bin2int(const char *bin, int len) 
{
    int i = 0, j;
    j = sizeof(int)*8;
    while ( (j--) && ((*bin=='0') || (*bin=='1')) && len ) {
        i <<= 1;
        if ( *bin=='1' ) i++;
        bin++;
        len--;
    }
    return i;
}

char *valtobin(u32 a, char *buffer, u32 len) {
    buffer[len] = '\0';
    buffer += len-1;
    for (int i = len-1; i >= 0; i--) {
        *buffer-- = (a & 1) + '0';
        a >>= 1;
    }
    return buffer;
}

static u32 wmi_addr_remap(u32 x)
{
	uint i;

	for (i = 0; i < ARRAY_SIZE(fw_mapping); i++) {
		if (fw_mapping[i].fw &&
		    ((x >= fw_mapping[i].from) && (x < fw_mapping[i].to)))
			return x + fw_mapping[i].host - fw_mapping[i].from;
	}

	return 0;
}

void *wmi_buffer(__le32 ptr_)
{
	u64 off;
	u64 ptr = le32_to_cpu(ptr_);

	if (ptr % 4)
		return NULL;

	ptr = wmi_addr_remap(ptr);
	if (ptr < WIL6210_FW_HOST_OFF)
		return NULL;

	off = HOSTADDR(ptr);
	return (void *)off;
}

void *wmi_addr(u64 ptr)
{
	u64 off;

	if (ptr % 4)
		return NULL;

	if (ptr < WIL6210_FW_HOST_OFF)
		return NULL;

	off = HOSTADDR(ptr);
	return (void *)off;
}

void wil_mbox_ring_le2cpus(struct wil6210_mbox_ring *r)
{
	le32_to_cpus(&r->base);
	le16_to_cpus(&r->entry_size);
	le16_to_cpus(&r->size);
	le32_to_cpus(&r->tail);
	le32_to_cpus(&r->head);
}

void wil_memcpy_fromio_32(void *dst, const void *src,
			  size_t count)
{
	u32 *d = dst;
	const u32 *s = src;

	for (; count >= 4; count -= 4)
		*d++ = *(s++);

	if (unlikely(count)) {
		/* count can be 1..3 */
		u32 tmp = *(s);

		memcpy(d, &tmp, count);
	}
}

void wil_memcpy_toio_32(void *dst, const void *src,
			size_t count)
{
	u32 *d = dst;
	const u32 *s = src;

	for (; count >= 4; count -= 4)
		*(d++) = *(s++);

	if (unlikely(count)) {
		/* count can be 1..3 */
		u32 tmp = 0;

		memcpy(&tmp, s, count);
		*d = tmp;
	}
}

void hex_dump_to_buffer(const void *buf, size_t len, int rowsize,
			int groupsize, char *linebuf, size_t linebuflen,
			bool ascii)
{
	const u8 *ptr = buf;
	u8 ch;
	int j, lx = 0;
	int ascii_column;

	if (rowsize != 16 && rowsize != 32)
		rowsize = 16;

	if (!len)
		goto nil;
	if (len > rowsize)		/* limit to one line at a time */
		len = rowsize;
	if ((len % groupsize) != 0)	/* no mixed size output */
		groupsize = 1;

	switch (groupsize) {
	case 8: {
		const u64 *ptr8 = buf;
		int ngroups = len / groupsize;

		for (j = 0; j < ngroups; j++)
			lx += snprintf(linebuf + lx, linebuflen - lx,
					"%s%16.16llx", j ? " " : "",
					(unsigned long long)*(ptr8 + j));
		ascii_column = 17 * ngroups + 2;
		break;
	}

	case 4: {
		const u32 *ptr4 = buf;
		int ngroups = len / groupsize;

		for (j = 0; j < ngroups; j++)
			lx += snprintf(linebuf + lx, linebuflen - lx,
					"%s%8.8x", j ? " " : "", *(ptr4 + j));
		ascii_column = 9 * ngroups + 2;
		break;
	}

	case 2: {
		const u16 *ptr2 = buf;
		int ngroups = len / groupsize;

		for (j = 0; j < ngroups; j++)
			lx += snprintf(linebuf + lx, linebuflen - lx,
					"%s%4.4x", j ? " " : "", *(ptr2 + j));
		ascii_column = 5 * ngroups + 2;
		break;
	}

	default:
		for (j = 0; (j < len) && (lx + 3) <= linebuflen; j++) {
			ch = ptr[j];
			linebuf[lx++] = hex_asc_hi(ch);
			linebuf[lx++] = hex_asc_lo(ch);
			linebuf[lx++] = ' ';
		}
		if (j)
			lx--;

		ascii_column = 3 * rowsize + 2;
		break;
	}
	if (!ascii)
		goto nil;

	while (lx < (linebuflen - 1) && lx < (ascii_column - 1))
		linebuf[lx++] = ' ';
	for (j = 0; (j < len) && (lx + 2) < linebuflen; j++) {
		ch = ptr[j];
		linebuf[lx++] = (isascii(ch) && isprint(ch)) ? ch : '.';
	}
nil:
	linebuf[lx++] = '\0';
}

void print_hex_dump(const char *prefix_str, int prefix_type,
		    int rowsize, int groupsize,
		    const void *buf, size_t len, bool ascii)
{
	const u8 *ptr = buf;
	int i, linelen, remaining = len;
	unsigned char linebuf[32 * 3 + 2 + 32 + 1];

	if (rowsize != 16 && rowsize != 32)
		rowsize = 16;

	for (i = 0; i < len; i += rowsize) {
		linelen = min(remaining, rowsize);
		remaining -= rowsize;

		hex_dump_to_buffer(ptr + i, linelen, rowsize, groupsize,
				   (char*) linebuf, sizeof(linebuf), ascii);

		switch (prefix_type) {
		case DUMP_PREFIX_ADDRESS:
			printf("%s%p: %s\n",
			       prefix_str, ptr + i, linebuf);
			break;
		case DUMP_PREFIX_OFFSET:
			printf("%s%.8x: %s\n", prefix_str, i, linebuf);
			break;
		default:
			printf("%s%s\n", prefix_str, linebuf);
			break;
		}
	}
}

void wil_hexdump(void *p, int len, const char *prefix)
{
	print_hex_dump(prefix, DUMP_PREFIX_NONE, 16, 1, p, len, false);
}

u64 open_phyaddr_to_virtaddr(u64 mem_address, size_t mem_size, void **base_addr, const char *pcie_path) {
	int fd;
	void *map_base, *virt_addr;
	u64 target = mem_address;
	size_t MAP_SIZE = mem_size;
	size_t PAGE_SIZE = sysconf(_SC_PAGESIZE);
	size_t MAP_MASK = (PAGE_SIZE - 1);
	
	if((fd = open(pcie_path, O_RDWR | O_SYNC)) == -1) PRINT_ERROR;
    // printf("Target offset is 0x%x, page size is %ld\n", (int) target, sysconf(_SC_PAGE_SIZE));
    fflush(stdout);
    
    /* Map one page */
    // printf("mmap(%d, %ld, 0x%x, 0x%x, %d, 0x%x)\n", 0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, (int) target);
    map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    if(map_base == (void *) -1) PRINT_ERROR;
    // printf("PCI Memory mapped to address 0x%08lx.\n", (unsigned long) map_base);
    fflush(stdout);
    close(fd);
	
	virt_addr = map_base + (target & MAP_MASK);
	*base_addr = map_base;
	printf("Open virtual memory address: %p\n", virt_addr);
	return (u64) virt_addr;
}

void close_phyaddr_to_virtaddr(void *map_base, size_t MAP_SIZE) {
	printf("Close virtual memory address: %p\n", map_base);
    if(munmap(map_base, MAP_SIZE) == -1) PRINT_ERROR;
}

void wil_print_ring(const u64 off_virt, const char *prefix)
{
    void *off = off_virt + HOST_MBOX + (void*) offsetof(struct wil6210_mbox_ctl, rx);
    
    struct wil6210_mbox_ring r;
	int rsize;
	uint i;
	
    wil_memcpy_fromio_32(&r, off, sizeof(r));
	wil_mbox_ring_le2cpus(&r);
	/*
	 * we just read memory block from NIC. This memory may be
	 * garbage. Check validity before using it.
	 */
	rsize = r.size / sizeof(struct wil6210_mbox_ring_desc);

	printf("ring %s = {\n", prefix);
	printf("  base = 0x%08x\n", r.base);
	printf("  size = 0x%04x bytes -> %d entries\n", r.size, rsize);
	printf("  tail = 0x%08x\n", r.tail);
	printf("  head = 0x%08x\n", r.head);
	printf("  entry size = %d\n", r.entry_size);
	
	if (r.size % sizeof(struct wil6210_mbox_ring_desc)) {
		printf("  ??? size is not multiple of %zd, garbage?\n",
			   sizeof(struct wil6210_mbox_ring_desc));
		goto out;
	}

	if (!wmi_addr(r.base) ||
	    !wmi_addr(r.tail) ||
	    !wmi_addr(r.head)) {
		printf("  ??? pointers are garbage?\n");
		goto out;
	}

	for (i = 0; i < rsize; i++) {
		struct wil6210_mbox_ring_desc d;
		struct wil6210_mbox_hdr hdr;
		size_t delta = i * sizeof(d);
		void *x = HOSTADDR((void *)(u64)r.base) + delta;

		// printf("r.base vir addr: %p\n", off_virt+(x-off));
		wil_memcpy_fromio_32(&d, x+off_virt, sizeof(d));

		printf("  [%2x] %s %s%s 0x%08x", i,
			   d.sync ? "F" : "E",
			   (r.tail - r.base == delta) ? "t" : " ",
			   (r.head - r.base == delta) ? "h" : " ",
			   le32_to_cpu(d.addr));


		void *src_d = wmi_buffer(d.addr);
		if (src_d && (u64)src_d != 0x40000) {
			wil_memcpy_fromio_32(&hdr, src_d + off_virt, sizeof(hdr));
			
			u16 len = le16_to_cpu(hdr.len);

			printf(" -> %04x %04x %04x %02x\n",
				   le16_to_cpu(hdr.seq), len,
				   le16_to_cpu(hdr.type), hdr.flags);
			if (len <= MAX_MBOXITEM_SIZE) {
				unsigned char databuf[MAX_MBOXITEM_SIZE];
				void *src_virt_d = src_d + off_virt + sizeof(struct wil6210_mbox_hdr);
				wil_memcpy_fromio_32(databuf, src_virt_d, len);
				wil_hexdump(databuf, len, "      : ");
			}
		} else {
			printf("\n");
		}
	}
 out:
	printf("}\n");
}

int __read_wmi(const u64 off_virt, u16 reply_id, void *databuf, u8 reply_size)
{
    void *off = off_virt + HOST_MBOX + (void*) offsetof(struct wil6210_mbox_ctl, rx);
    
    struct wil6210_mbox_ring r;
	int rsize;
	uint i;
	struct wmi_cmd_hdr *cmd_hdr;
	
    wil_memcpy_fromio_32(&r, off, sizeof(r));
	wil_mbox_ring_le2cpus(&r);
	/*
	 * we just read memory block from NIC. This memory may be
	 * garbage. Check validity before using it.
	 */
	rsize = r.size / sizeof(struct wil6210_mbox_ring_desc);
	
	if (r.size % sizeof(struct wil6210_mbox_ring_desc)) {
		printf("  ??? size is not multiple of %zd, garbage?\n",
			   sizeof(struct wil6210_mbox_ring_desc));
		return 0;
	}

	if (!wmi_addr(r.base) ||
	    !wmi_addr(r.tail) ||
	    !wmi_addr(r.head)) {
		printf("  ??? pointers are garbage?\n");
		return 0;
	}

	for (i = 0; i < rsize; i++) {
		struct wil6210_mbox_ring_desc d;
		struct wil6210_mbox_hdr hdr;
		size_t delta = i * sizeof(d);
		void *x = HOSTADDR((void *)(u64)r.base) + delta;
		wil_memcpy_fromio_32(&d, x+off_virt, sizeof(d));

		void *src_d = wmi_buffer(d.addr);
		if (src_d && (u64)src_d != 0x40000) {
			wil_memcpy_fromio_32(&hdr, src_d + off_virt, sizeof(hdr));
			
			u16 len = le16_to_cpu(hdr.len);

			if (len <= MAX_MBOXITEM_SIZE) {
				void *src_virt_d = src_d + off_virt + sizeof(struct wil6210_mbox_hdr);
				wil_memcpy_fromio_32(databuf, src_virt_d, len);
				cmd_hdr = (struct wmi_cmd_hdr *) databuf;
				if (cmd_hdr->command_id == reply_id) {
					return len;
				}
				if (cmd_hdr->command_id == 0xffff) {
					printf("NOT_SUPPORTED_EVENTID detected!!\n");
				}
			}
		}
	}
	
	return 0;
}

void mem_read_data(void *buf, const void * addr, u8 size) {
	u32 data = 0;
	u64 addr_aligned = ((u64) addr)/0x4*0x4;
	u8 byte_offset = ((u64) addr) - addr_aligned;
	void *p = (void *)&data;
	
	wil_memcpy_fromio_32(p, (void *) addr_aligned, 4);
	size = size > 4-byte_offset ? 4-byte_offset : size;
	memcpy(buf, (void *)p+byte_offset, size);
}

void __mem_dump(const void * addr, u32 size, unsigned char *databuf) {
	u64 addr_aligned = ((u64) addr)/0x4*0x4;
	
	#ifdef MBC_DEBUG
    printf("dump memory from: %p\n", (void *) addr_aligned);
    #endif
	wil_memcpy_fromio_32(databuf, (void *) addr_aligned, size);
	// wil_hexdump(databuf, size, "");
}

static PyObject *
open_wmi_dev(PyObject *self, PyObject *args)
{
    const char *pcie_path;
    if (!PyArg_ParseTuple(args, "s", &pcie_path))
    {
        return NULL;
    }
    
	void *base_addr;
	u64 off_virt = (u64) open_phyaddr_to_virtaddr(0, 2048000, &base_addr, pcie_path);
    
    return Py_BuildValue("z#", (char *) &off_virt, sizeof(u64));
}

static PyObject *
close_wmi_dev(PyObject *self, PyObject *args)
{
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "z#", &instr, &size))
    {
        return NULL;
    }
    
    u64 base_addr;
    if (size == sizeof(u64)) {
	    memcpy(&base_addr, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    close_phyaddr_to_virtaddr((void *) base_addr, 2048000);
    
    Py_RETURN_NONE;
}

static PyObject *
wil_print_ring_rx(PyObject *self, PyObject *args)
{
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "z#", &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    
    wil_print_ring(off_virt, "rx");
    
    Py_RETURN_NONE;
}

static PyObject *
read_wmi(PyObject *self, PyObject *args)
{
    u16 reply_id;
    u32 trynum;
    u32 to_msec;
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "HIIz#", &reply_id, &trynum, &to_msec, &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    unsigned char databuf[MAX_MBOXITEM_SIZE];
    
    int len = 0;
    do {
    	usleep(to_msec*1000);
    	len = __read_wmi(off_virt, reply_id, databuf, MAX_MBOXITEM_SIZE);
    } while (len == 0 && printf("event 0x%04x no response.\n", reply_id) && --trynum > 0);

    if (len > 0) {
    	return Py_BuildValue("z#", databuf + sizeof(struct wil6210_mbox_hdr), max(len-sizeof(struct wil6210_mbox_hdr), 0));
    } else {
    	Py_RETURN_NONE;
    }
}

static PyObject *
mem_read(PyObject *self, PyObject *args)
{
    u32 addr = 0;
    u32 read_len = 0;
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "IIz#", &addr, &read_len, &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    
    if (read_len >= 4) read_len = 4;
    else if (read_len >= 2) read_len = 2;
    else read_len = 1;
    u32 buf = 0;
    mem_read_data(&buf, HOSTADDR(((void *) off_virt) + addr), read_len);
   
    return Py_BuildValue("I", buf);
}

static PyObject *
mem_write(PyObject *self, PyObject *args) 
{
	u32 addr = 0;
	u32 data = 0;
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "IIz#", &data, &addr, &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    
    void * dst_addr = HOSTADDR(((void *) off_virt) + addr);
	u64 addr_aligned = ((u64) dst_addr)/0x4*0x4;
	
    printf("write %x to memory: %p\n", data, (void *) addr_aligned);
	wil_memcpy_toio_32((void *) addr_aligned, (void *) &data, 4);
	
	Py_RETURN_NONE;
}

struct mem_block_write_data {
    u64 off_virt;
	u32 addr;
	u32 size;
	u32 data[];
};

static PyObject *
mem_block_write(PyObject *self, PyObject *args) 
{
	struct mem_block_write_data *in_params;
    int size;
    // const char *instr;
    
    if (!PyArg_ParseTuple(args, "z#", &in_params, &size))
    {
        return NULL;
    }
    
    // printf("(%u) %lu\n", in_params->addr, in_params->off_virt);
    // printf("%u\n", in_params->size);
    
    void * dst_addr = HOSTADDR(((void *) in_params->off_virt) + in_params->addr);
	u64 addr_aligned = ((u64) dst_addr)/0x4*0x4;
	in_params->size = in_params->size * 4;
	
    printf("write %u bytes to memory: %p\n", in_params->size, (void *) addr_aligned);
	wil_memcpy_toio_32((void *) addr_aligned, (void *) in_params->data, in_params->size);
    
	Py_RETURN_NONE;
}

static PyObject *
mem_dump(PyObject *self, PyObject *args)
{
    u32 addr = 0;
    u32 read_len = 0;
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "IIz#", &addr, &read_len, &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    
	unsigned char databuf[read_len];
	#ifdef MBC_DEBUG
    printf("dump physical addr: %p\n", (void *) (u64) addr);
    #endif
    __mem_dump(HOSTADDR(((void *) off_virt) + addr), read_len, databuf);
    
    return Py_BuildValue("z#", databuf, read_len);
}

static PyObject *
us_sleep(PyObject *self, PyObject *args)
{
    u32 sleep_duration;
    if (!PyArg_ParseTuple(args, "I", &sleep_duration))
    {
        return NULL;
    }
    
    usleep(sleep_duration);
    
    Py_RETURN_NONE;
}

static PyObject * 
convert_sector_cfg(PyObject *self, PyObject *args) {
    const char *instr;
    int size;
	struct wmi_rf_sector_info si;
    if (!PyArg_ParseTuple(args, "z#", &instr, &size))
    {
        return NULL;
    }
    
    if (size < sizeof(struct wmi_rf_sector_info)) {
    	return NULL;
    } else {
		memcpy(&si, instr, sizeof(struct wmi_rf_sector_info));
    }
    
	char binary_etype0[33];
	char binary_etype1[33];
	char binary_etype2[33];
	char binary_psh_hi[33];
	char binary_psh_lo[33];
	char binary_dtype_swch_off[33];
	int i;
	char binary_etype[3];
	char binary_phase[2];
	PyObject *list, *item;
	list = PyList_New(0);
	long tmp;
	
	u32tobin(si.etype0, binary_etype0);
	#ifdef MBC_DEBUG
	printf("ETYPE Bit0 for all RF chains[31-0] - bit0 of Edge amplifier gain index.\n");
	printf("etype0: %s (%d) (0x%08x)\n", binary_etype0, si.etype0, si.etype0);
	#endif
		
	u32tobin(si.etype1, binary_etype1);
	#ifdef MBC_DEBUG
	printf("ETYPE Bit1 for all RF chains[31-0] - bit1 of Edge amplifier gain index.\n");
	printf("etype1: %s (%d) (0x%08x)\n", binary_etype1, si.etype1, si.etype1);
	#endif
		
	u32tobin(si.etype2, binary_etype2);
	#ifdef MBC_DEBUG
	printf("ETYPE Bit2 for all RF chains[31-0] - bit2 of Edge amplifier gain index.\n");
	printf("etype2: %s (%d) (0x%08x)\n", binary_etype2, si.etype2, si.etype2);
	#endif
		
	u32tobin(si.psh_hi, binary_psh_hi);
	#ifdef MBC_DEBUG
	printf("Phase values for RF Chains[15-0] (2bits per RF chain).\n");
	printf("psh_hi: %s (%d) (0x%08x)\n", binary_psh_hi, si.psh_hi, si.psh_hi);
	#endif
		
	u32tobin(si.psh_lo, binary_psh_lo);
	#ifdef MBC_DEBUG
	printf("Phase values for RF Chains[31-16] (2bits per RF chain).\n");
	printf("psh_lo: %s (%d) (0x%08x)\n", binary_psh_lo, si.psh_lo, si.psh_lo);
	#endif
		
	u32tobin(si.dtype_swch_off, binary_dtype_swch_off);
	#ifdef MBC_DEBUG
	printf("D-Type values (3bits each) for 8 Distribution amplifiers + X16 switch bits.\n");
	printf("dtype_swch_off: %s (%d) (0x%08x)\n", binary_dtype_swch_off, si.dtype_swch_off, si.dtype_swch_off);
	#endif
	
	#ifdef MBC_DEBUG
	printf("Gain magnitude: ");
	#endif
	for(i = 0; i < 32; i++) {
		binary_etype[2] = binary_etype0[i];
		binary_etype[1] = binary_etype1[i];
		binary_etype[0] = binary_etype2[i];
		tmp = bin2int(binary_etype, 3);
		#ifdef MBC_DEBUG
		printf("%ld", tmp);
		#endif
		item = PyLong_FromLong(tmp);
		PyList_Append(list, item);
	}
	#ifdef MBC_DEBUG
	printf("\n");
	#endif
	
	#ifdef MBC_DEBUG
	printf("Phase shifting: ");
	#endif
	for(i = 0; i < 32; i+=2) {
		binary_phase[0] = binary_psh_hi[i];
		binary_phase[1] = binary_psh_hi[i+1];
		tmp = bin2int(binary_phase, 2);
		#ifdef MBC_DEBUG
		printf("%ld", tmp);
		#endif
		item = PyLong_FromLong(tmp);
		PyList_Append(list, item);
	}
	for(i = 0; i < 32; i+=2) {
		binary_phase[0] = binary_psh_lo[i];
		binary_phase[1] = binary_psh_lo[i+1];
		tmp = bin2int(binary_phase, 2);
		#ifdef MBC_DEBUG
		printf("%ld", tmp);
		#endif
		item = PyLong_FromLong(tmp);
		PyList_Append(list, item);
	}
	#ifdef MBC_DEBUG
	printf("\n");
	#endif
	
	#ifdef MBC_DEBUG
	printf("Group amplifier: ");
	#endif
	for(i = 8; i < 32; i+=3) {
		tmp = bin2int(binary_dtype_swch_off+i, 3);
		#ifdef MBC_DEBUG
		printf("%ld", tmp);
		#endif
		item = PyLong_FromLong(tmp);
		PyList_Append(list, item);
	}
	#ifdef MBC_DEBUG
	printf("\n");
	#endif
	
    return list;
}

static PyObject * 
cfg_verify_convert(PyObject *self, PyObject *args) {
    const char *instr;
    int size;
	char mag[33], phase[33], amp[9];
    if (!PyArg_ParseTuple(args, "z#", &instr, &size))
    {
        return NULL;
    }
    
    if (size != 72) {
    	printf("parameter invalid %u", size);
    	return NULL;
    } else {
		memcpy(mag, instr, 32);
		memcpy(phase, instr+32, 32);
		memcpy(amp, instr+64, 8);
    }
    mag[32] = '\0';
    phase[32] = '\0';
    amp[8] = '\0';
	
	struct wmi_rf_sector_info cfg;
	int i;
	char buf_etype0[33];
	char buf_etype1[33];
	char buf_etype2[33];
	u32 etype;
	char etype_bits[4];
	u32 etypes[3];
	
	char buf_psh_hi[33];
	char buf_psh_lo[33];
	u32 psh;
	char psh_bits[3];
	u32 pshs[2];
	
	char buf_amp[33];
	u32 am;
	char am_bits[4];
	
	#ifdef MBC_DEBUG
	printf("mag: %s\n", mag);
	printf("phase: %s\n", phase);
	printf("amp: %s\n", amp);
	#endif
	
	if (strlen(mag) != 32) {
		printf("mag length %lu is not equal to 32\n", (long unsigned int)strlen(mag));
    	Py_RETURN_NONE;
	} else {
		buf_etype0[32] = '\0';
		buf_etype1[32] = '\0';
		buf_etype2[32] = '\0';
		
		for (i = 0; i < 32; i++) {
			etype = mag[i] - '0';
			if (etype < 0 || etype > 7) {
				printf("mag range should be 0-7.\n");
    			Py_RETURN_NONE;
			} else {
				valtobin(etype, etype_bits, 3);
				buf_etype0[i] = etype_bits[2];
				buf_etype1[i] = etype_bits[1];
				buf_etype2[i] = etype_bits[0];
			}
		}
	}
	
	etypes[0] = bin2int(buf_etype0, 32);
	etypes[1] = bin2int(buf_etype1, 32);
	etypes[2] = bin2int(buf_etype2, 32);
	cfg.etype0 = etypes[0];
	cfg.etype1 = etypes[1];
	cfg.etype2 = etypes[2];
	
	#ifdef MBC_DEBUG
	printf("buf_etype0: %s (0x%08x)\n", buf_etype0, etypes[0]);
	printf("buf_etype1: %s (0x%08x)\n", buf_etype1, etypes[1]);
	printf("buf_etype2: %s (0x%08x)\n", buf_etype2, etypes[2]);
	#endif
	
	if (strlen(phase) !=32) {
		printf("phase length %lu is not equal to 32\n", (long unsigned int)strlen(phase));
    	Py_RETURN_NONE;
	} else {
		buf_psh_hi[32] = '\0';
		buf_psh_lo[32] = '\0';
		
		for (i = 0; i < 32; i++) {
			psh = phase[i] - '0';
			if (psh < 0 || psh > 3){
				printf("phase range is 0-3.\n");
    			Py_RETURN_NONE;
			} else {
				valtobin(psh, psh_bits, 2);
				if (i < 16) {
					buf_psh_hi[i*2] = psh_bits[0];
					buf_psh_hi[i*2+1] = psh_bits[1];
				} else {
					buf_psh_lo[(i-16)*2] = psh_bits[0];
					buf_psh_lo[(i-16)*2+1] = psh_bits[1];
				}
			}
		}
	}
	
	pshs[0] = bin2int(buf_psh_lo, 32);
	cfg.psh_lo = pshs[0];
	pshs[1] = bin2int(buf_psh_hi, 32);
	cfg.psh_hi = pshs[1];
	
	#ifdef MBC_DEBUG
	printf("buf_psh_hi: %s (0x%08x)\n", buf_psh_hi, pshs[1]);
	printf("buf_psh_lo: %s (0x%08x)\n", buf_psh_lo, pshs[0]);
	#endif
	
	if (strlen(amp) != 8) {
		printf("group amplifier length %lu is not equal to 8\n", (long unsigned int)strlen(amp));
    	Py_RETURN_NONE;
	} else {
		buf_amp[32] = '\0';
		strcpy(buf_amp, "00110000");
		for (i = 0; i < 8; i++) {
			am = amp[i] - '0';
			if (am < 0 || am > 7) {
				printf("group amplifier range is 0-7.\n");
    			Py_RETURN_NONE;
			} else {
				valtobin(am, am_bits, 3);
				buf_amp[i*3+8] = am_bits[0];
				buf_amp[i*3+9] = am_bits[1];
				buf_amp[i*3+10] = am_bits[2];
			}
		}
	}
	
	am = bin2int(buf_amp, 32);
	cfg.dtype_swch_off = am;
	
	#ifdef MBC_DEBUG
	printf("buf_amp: %s (0x%08x)\n", buf_amp, am);
	#endif
	
    return Py_BuildValue("z#", &cfg, sizeof(struct wmi_rf_sector_info));
}

static inline size_t log_size(size_t entry_num)
{
	return sizeof(struct log_table_header) + entry_num * 4;
}

static PyObject * 
get_fw_trace(PyObject *self, PyObject *args) {
	static u32 rptr; /* = 0; */
	static size_t log_buf_entries = 0x1000/4; /* entries in the log buf */
	static void *log_buf; /* memory allocated for the log buf */
	
	/* get fw trace */
    u32 addr = 0;
    u32 read_len = 0;
    const char *instr;
    int size;
    if (!PyArg_ParseTuple(args, "IIz#", &addr, &read_len, &instr, &size))
    {
        return NULL;
    }
    
    u64 off_virt;
    if (size == sizeof(u64)) {
	    memcpy(&off_virt, instr, sizeof(u64));
    } else {
    	printf("size %d mismatch\n", size);
    }
    
    log_buf_entries = read_len;
    u32 buf_size = log_size(log_buf_entries);
	log_buf = malloc(buf_size);
	#ifdef MBC_DEBUG
    printf("dump physical addr: %p\n", (void *) (u64) addr);
    #endif
    __mem_dump(HOSTADDR(((void *) off_virt) + addr), buf_size, log_buf);
	
	/* parse fw trace */
	#ifdef MBC_DEBUG
    printf("parsing fw trace\n");
    #endif
	struct log_table_header *h = log_buf;
	u32 wptr = h->write_ptr;
	if ((wptr - rptr) >= log_buf_entries) {
		#ifdef MBC_DEBUG
		printf("overflow; try to parse last wrap.\n");
    	#endif
		/* overflow; try to parse last wrap */
		rptr = wptr - log_buf_entries;
	}
	
	PyObject *log_list, *log_entry;
	log_list = PyList_New(0);
	for (; (s32)(wptr - rptr) > 0; rptr++) {
		int i;
		u32 p[3] = {0};
		union log_event *evt = &h->evt[rptr % log_buf_entries];
		if (evt->hdr.signature != 5)
			continue;
		if (evt->hdr.parameters_num > 3)
			continue;
		for (i = 0; i < evt->hdr.parameters_num; i++)
			p[i] = h->evt[(rptr + i + 1) % log_buf_entries].param;

		#ifdef MBC_DEBUG
		printf("[%6d] %u %u(0x%08x) :", rptr, evt->hdr.module,
				evt->hdr.level, evt->hdr.strring_offset);
		if (evt->hdr.parameters_num == 0) {
			printf(" ");
		} else if (evt->hdr.parameters_num == 1) {
			printf("%u", p[0]);
		} else if (evt->hdr.parameters_num == 2) {
			printf("%u, %u", p[0], p[1]);
		} else if (evt->hdr.parameters_num == 3) {
			printf("%u, %u, %u", p[0], p[1], p[2]);
		}
		printf("\n");
    	#endif
		
		log_entry = PyList_New(0);
		PyList_Append(log_entry, PyLong_FromUnsignedLong(rptr));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(evt->hdr.module));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(evt->hdr.level));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(evt->hdr.strring_offset));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(evt->hdr.parameters_num));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(p[0]));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(p[1]));
		PyList_Append(log_entry, PyLong_FromUnsignedLong(p[2]));
		
		PyList_Append(log_list, log_entry);
		
		rptr += evt->hdr.parameters_num;
	}
	#ifdef MBC_DEBUG
	fflush(stdout);
    #endif
	
	free(log_buf);
	
	return log_list;
}

static PyMethodDef Wil6210MailboxMethods[] = {
    {"read_wmi", read_wmi, METH_VARARGS, "read wmi event."},
    {"wil_print_ring_rx", wil_print_ring_rx, METH_VARARGS, "print rx mailbox."},
    {"mem_read", mem_read, METH_VARARGS, "read memory data."},
    {"mem_dump", mem_dump, METH_VARARGS, "dump memory data."},
    {"mem_write", mem_write, METH_VARARGS, "write memory data."},
    {"mem_block_write", mem_block_write, METH_VARARGS, "write memory data in buck."},
    {"open_wmi_dev", open_wmi_dev, METH_VARARGS, "open wmi device."},
    {"close_wmi_dev", close_wmi_dev, METH_VARARGS, "close wmi device."},
    {"us_sleep", us_sleep, METH_VARARGS, "sleep microseconds in C."},
    {"convert_sector_cfg", convert_sector_cfg, METH_VARARGS, 
    	"Convert get sector pattern configuration information."},
    {"cfg_verify_convert", cfg_verify_convert, METH_VARARGS, 
    	"Convert set sector pattern configuration information."},
    {"get_fw_trace", get_fw_trace, METH_VARARGS, "Get firmware trace."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initwil6210_mbc(void)
{
    (void) Py_InitModule("wil6210_mbc", Wil6210MailboxMethods);
}

PyMODINIT_FUNC
initwil6210_mbc_armv7l(void)
{
    (void) Py_InitModule("wil6210_mbc_armv7l", Wil6210MailboxMethods);
}

PyMODINIT_FUNC
initwil6210_mbc_x86_64(void)
{
    (void) Py_InitModule("wil6210_mbc_x86_64", Wil6210MailboxMethods);
}