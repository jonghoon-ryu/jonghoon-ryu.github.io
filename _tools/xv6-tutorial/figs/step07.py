from svg import D


def rings():
    d = D(1000, 330, "Talking to the xHCI: rings in memory + doorbell registers")
    d.text(20, 58, "memory (DMA: the controller reads and writes it directly)", 12, True, "start", "#2c3e50")
    def ring(x, y, label, kind, n=7, filled=3, link=True):
        d.text(x, y - 6, label, 11.5, True, "start", "#2c3e50")
        for i in range(n):
            last = link and i == n - 1
            d.box(x + i * 52, y, 48, 34, "", ["Link"] if last else ["TRB"], "gray" if last else (kind if i < filled else "white"), size=11, rx=2)
        d.path(f"M{x + (n - 1) * 52 + 24},{y + 34} L{x + (n - 1) * 52 + 24},{y + 48} L{x + 24},{y + 48} L{x + 24},{y + 36}")
    ring(20, 90, "command ring (cmdring): CPU → controller", "new")
    ring(20, 190, "event ring (evring): controller → CPU (wraps without a Link)", "hw", filled=2, link=False)
    d.box(440, 80, 230, 60, "CPU", ["Ring::push() writes a TRB,", "db[0] = 0 (doorbell)"], "base", size=12)
    d.box(440, 180, 230, 60, "CPU: poll()", ["reads TRBs whose cycle bit matches,", "writes ERDP: how far it has read"], "base", size=11.5)
    d.box(740, 80, 240, 160, "xHCI controller", ["on a doorbell, reads", "and runs the command ring", "", "writes results, port changes,", "transfer completions to the event ring"], "hw", size=12)
    d.arrow(670, 110, 738, 110, "doorbell"); d.arrow(738, 210, 672, 210, "events")
    d.box(20, 268, 960, 52, "", ["TRB = 16 bytes: param (64) · status (32) · control (32; bit 0 = cycle, bits 15:10 = type)", "command/transfer ring = one page = 255 TRBs + a Link TRB.  event ring = one page = 256 TRBs (no Link)"], "white", size=12)
    return d.svg("command and event rings")


def cycle():
    d = D(1000, 250, "The cycle bit: marks 'new on this lap' (producer and consumer agree without a shared count)")
    for r, label in enumerate(["first lap: producer cycle = 1", "after passing the Link: cycle = 0 (flipped)"]):
        y = 60 + r * 90
        d.text(20, y - 6, label, 11.5, True, "start", "#2c3e50")
        for i in range(8):
            if r == 0:
                c = 1 if i < 5 else 0; k = "new" if i < 5 else "white"
            else:
                c = 0 if i < 3 else 1; k = "chg" if i < 3 else "gray"
            d.box(20 + i * 60, y, 56, 40, "", [f"c={c}"], k, size=11.5, rx=2, mono=True)
        d.text(520, y + 25, "← new: TRBs whose cycle equals what the consumer expects" if r == 0 else "← TRBs from the last lap (c=1) are now 'old'", 11, False, "start")
    d.box(20, 200, 960, 40, "", ["push() writes param and status first and the control word (with cycle) last, so the controller never sees a half-written TRB as new"], "white", size=12)
    return d.svg("cycle bit")


def init():
    d = D(1000, 230, "The order in Xhci::init() (xHCI 4.2)")
    x = 15
    for i, (t, ls, k) in enumerate([("PCI", ["memory decode,", "bus master on"], "base"), ("ismapped()", ["registers in the", "firmware page tables?"], "hw"),
                                    ("handoff()", ["take over from", "the firmware"], "hw"), ("reset()", ["halt → HCRST", "→ wait until ready"], "chg"),
                                    ("memory", ["DCBAA, scratchpad", "command, event ring"], "new"), ("Run", ["USBCMD.RS = 1", "port power"], "new")]):
        d.box(x, 60, 150, 80, t, ls, k, size=12)
        if i:
            d.arrow(x - 15, 100, x - 1, 100)
        x += 165
    d.box(15, 165, 970, 50, "", ["real PC (Intel 8086:7a60): registers at 0x6001100000 (above 4 GB), 34 scratchpad pages. QEMU: 0xc000000000, no scratchpad"], "white", size=12)
    return d.svg("init order")


def loop():
    d = D(1000, 300, "The bug the real PC found: port reset → port change event → reset again …")
    d.box(20, 70, 200, 70, "port change event", ["marked in portpending"], "hw")
    d.box(280, 70, 200, 70, "portchange(port)", ["connected → reset"], "chg")
    d.box(540, 70, 200, 70, "port reset (PR)", ["sets PRC when done"], "hw")
    d.box(800, 70, 180, 70, "device setup", ["not a keyboard → ignored"], "gray")
    d.arrow(220, 105, 278, 105); d.arrow(480, 105, 538, 105); d.arrow(740, 105, 798, 105)
    d.path("M640,140 L640,175 L120,175 L120,142", color="#c0392b")
    d.text(380, 192, "'reset finished' also arrives as a port change event → start over (forever)", 11.5, color="#c0392b")
    d.box(20, 215, 960, 65, "Fix: porthandled[port]", ["a port looked at once per connection (set up, ignored or failed) is not looked at again; cleared on disconnect",
                                                      "QEMU had only keyboards and hubs, so it never showed. The real PC's built-in MSI device (db0:76) did"], "new", size=12)
    return d.svg("endless loop bug")


def portsc():
    d = D(1000, 300, "PORTSC (port status and control): 0xee1 before reset, 0xe03 after (read in QEMU)")
    f = [(31, 22, "…", "gray", 3), (21, 21, "PRC", "chg", 2), (20, 18, "…", "gray", 2), (17, 17, "CSC", "chg", 2), (16, 14, "…", "gray", 2),
         (13, 10, "speed", "base", 3), (9, 9, "PP", "base", 2), (8, 5, "link state", "base", 3), (4, 4, "PR", "new", 2), (3, 2, "…", "gray", 1), (1, 1, "PED", "new", 2), (0, 0, "CCS", "new", 2)]
    d.bits(150, 60, 820, 0, f, h=40, label="0xee1", value=0xee1)
    d.bits(150, 160, 820, 0, f, h=40, label="0xe03", value=0xe03)
    d.text(560, 252, "CCS connected · PED enabled (writing 1 disables it!) · PR reset · link state 7 (Polling) → 0 (U0) · PP power · speed 3 = high", 11.5)
    d.text(560, 276, "'change' bits such as CSC and PRC are cleared by writing 1 (RW1C) → neutral() drops the dangerous bits before writing", 11.5)
    return d.svg("PORTSC bits")


def regspace():
    d = D(1000, 380, "The xHCI register spaces, starting at BAR0")
    y = 50
    for name, regs, k in [("capability (base + 0)", "CAPLENGTH, HCSPARAMS1/2, HCCPARAMS1, DBOFF, RTSOFF", "base"),
                          ("operational (base + CAPLENGTH)", "USBCMD, USBSTS, PAGESIZE, CRCR, DCBAAP, CONFIG, PORTSC[n] (0x400 + 0x10·(n−1))", "chg"),
                          ("runtime (base + RTSOFF)", "interrupter 0: ERSTSZ (+0x28), ERSTBA (+0x30), ERDP (+0x38)", "mem"),
                          ("doorbell (base + DBOFF)", "db[0] = command ring, db[slot] = that device's endpoint number", "new"),
                          ("extended caps (HCCPARAMS1 31:16 × 4)", "ID 1: USB Legacy Support (handoff) → ID 2: Supported Protocol (USB 2 / 3 ports)", "hw")]:
        d.box(20, y, 300, 52, name, [], k, size=12)
        d.text(335, y + 31, regs, 11.5, False, "start")
        y += 60
    d.text(500, 368, "Xhci::init() keeps these as the base, op, rt and db pointers. QEMU's extended capabilities are just two ID 2 entries (nothing to hand off)", 11.5)
    return d.svg("xHCI register spaces")


def dcbaa():
    d = D(1000, 250, "DCBAA: one device-context address per slot; entry 0 is the scratchpad")
    for i in range(6):
        d.rect(60, 50 + i * 30, 160, 30, "mem" if i else "hw")
        d.text(140, 70 + i * 30, f"dcbaa[{i}]" + ("  scratchpad" if i == 0 else ""), 11, mono=True)
    d.text(140, 240, "one page (DCBAAP register)", 10.5)
    d.box(300, 40, 260, 70, "scratchpad array", ["sp[0], sp[1], … sp[33]", "(real PC: 34 pages, QEMU: 0)"], "hw", size=12)
    d.box(620, 40, 340, 70, "34 pages", ["memory the controller keeps for itself;", "software never touches it"], "gray", size=12)
    d.arrow(220, 65, 298, 75); d.arrow(560, 75, 618, 75)
    d.box(300, 140, 660, 70, "dcbaa[slot] → that device's device (output) context", ["filled by newdev() in step-08; the Enable Slot command gives the slot number"], "new", size=12)
    d.arrow(220, 95, 298, 175)
    return d.svg("DCBAA")
