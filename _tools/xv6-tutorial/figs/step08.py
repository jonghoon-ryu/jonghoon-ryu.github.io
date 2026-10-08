from svg import D


def enum():
    d = D(1000, 520, "Getting to know a new device (usbattach): commands go to the controller, requests to the device")
    for name, x in [("usb.cpp / xhci.cpp", 110), ("xHCI controller", 480), ("USB device", 820)]:
        d.box(x - 90, 45, 180, 32, name, [], "hw" if x > 300 else "base", size=12)
        d.line(x, 77, x, 465, "#d5dbdb", 2, True)
    msgs = [(110, 480, "Enable Slot command", "→ slot number", "new"), (110, 480, "Address Device command (input context)", "", "new"),
            (480, 820, "SET_ADDRESS (sent by the controller)", "", "hw"), (110, 820, "GET_DESCRIPTOR device, 8 bytes", "→ endpoint 0 size", "chg"),
            (110, 480, "(if needed) Evaluate Context", "", "new"), (110, 820, "GET_DESCRIPTOR device, 18 bytes", "→ vendor, product, class", "chg"),
            (110, 820, "GET_DESCRIPTOR config, 9 bytes → all", "→ interfaces, endpoints", "chg")]
    y = 105
    for a, b, lab, ret, k in msgs:
        d.arrow(a, y, b - 4, y, color="#1e8449" if k == "new" else "#7d3c98" if k == "hw" else "#b7950b")
        d.text((a + b) / 2, y - 6, lab, 11)
        if ret:
            d.arrow(b, y + 16, a + 4, y + 16, dash=True); d.text((a + b) / 2, y + 30, ret, 10.5, color="#566573")
            y += 60
        else:
            y += 40
    d.box(20, 470, 960, 40, "", ["green = xHCI commands (command ring),  yellow = USB control transfers (the device's endpoint 0 ring),  purple = sent by the controller itself"], "white", size=12)
    return d.svg("device setup sequence")


def control():
    d = D(1000, 240, "A control transfer = three TRBs on endpoint 0's ring")
    d.box(20, 60, 300, 100, "Setup TRB", ["the 8-byte request inside the TRB (IDT)", "bmRequestType, bRequest,", "wValue, wIndex, wLength"], "chg", size=12)
    d.box(350, 60, 300, 100, "Data TRB (if any)", ["buffer address d.buf, length", "direction IN (device → host)", "or OUT"], "chg", size=12)
    d.box(680, 60, 300, 100, "Status TRB", ["opposite direction to the data", "IOC: transfer event when done", "→ ctldone = true"], "chg", size=12)
    d.arrow(320, 110, 348, 110); d.arrow(650, 110, 678, 110)
    d.box(20, 180, 960, 45, "", ["db[slot] = 1 (endpoint 0's doorbell). An unknown request gets a STALL (completion code 6) → resetep(): Reset Endpoint + Set TR Dequeue"], "white", size=12)
    return d.svg("control transfer")


def desc():
    d = D(1000, 250, "Device descriptor, 18 bytes (QEMU's USB keyboard, as read)")
    b = "12 01 00 02 00 00 00 40 27 06 01 00 00 00 01 04 0b 01".split()
    names = ["bLength", "type", "bcdUSB", "", "class", "sub", "proto", "mps0", "idVendor", "", "idProduct", "", "release", "", "iManu", "iProd", "iSerial", "nConf"]
    kinds = ["gray", "gray", "base", "base", "chg", "chg", "chg", "new", "hw", "hw", "hw", "hw", "gray", "gray", "base", "base", "base", "gray"]
    for i, v in enumerate(b):
        d.box(20 + i * 53, 60, 50, 40, "", [v], kinds[i], mono=True, size=13, rx=2)
        d.text(20 + i * 53 + 25, 54, str(i), 9.5, mono=True)
        if names[i]:
            d.text(20 + i * 53 + (51 if names[i] in ("bcdUSB", "idVendor", "idProduct", "release") else 25), 118, names[i], 10)
    d.box(20, 140, 960, 90, "", ["bcdUSB 0x0200 = USB 2.0,  mps0 0x40 = endpoint 0 up to 64 bytes,  vendor 0x0627 / product 0x0001 (little-endian: 27 06 → 0x0627)",
                                  "class 0 = decided per interface → look in the configuration's interfaces for class 3 (HID), subclass 1 (boot), protocol 1 (keyboard)",
                                  "the real PC's keyboard: id 4d9:a0f8 (a Holtek chip), full speed"], "white", size=12)
    return d.svg("device descriptor")


def contexts():
    d = D(1000, 430, "Input context and device context (32-byte entries; Address Device as the example)")
    d.text(250, 50, "input context (inctx): written by software", 12.5, True, color="#2c3e50")
    y = 62
    for a, b, k in [("0: input control", "add flags = A0 | A1 (slot + EP0)", "chg"), ("1: slot", "route, speed, 1 entry, root port, TT", "new"),
                    ("2: EP0 (DCI 1)", "type Control, mps0, ring address | 1", "new"), ("3…: other endpoints", "(step-09: the keyboard's IN endpoint)", "gray")]:
        d.box(20, y, 170, 44, "", [a], k, size=11.5, rx=0)
        d.box(190, y, 300, 44, "", [b], "white", size=11, rx=0)
        y += 44
    d.text(760, 50, "device context (outctx): written by the controller", 12.5, True, color="#2c3e50")
    y = 62
    for a, b in [("0: slot", "slot state, USB address (dw3 7:0)"), ("1: EP0", "endpoint state"), ("2…: EP1 OUT, IN, …", "")]:
        d.box(540, y, 170, 44, "", [a], "mem", size=11.5, rx=0)
        d.box(710, y, 270, 44, "", [b], "white", size=11, rx=0)
        y += 44
    d.text(760, 210, "↑ dcbaa[slot] points to this page", 11)
    d.text(500, 255, "slot context, dwords 0 – 2", 12.5, True, color="#2c3e50")
    d.bits(120, 280, 840, 32, [(31, 27, "entries", "chg"), (26, 26, "Hub", "base", 2), (25, 24, "", "gray", 1), (23, 20, "speed", "new"), (19, 0, "route string", "mem", 10)], h=30, label="dw0")
    d.bits(120, 335, 840, 32, [(31, 24, "ports (hub)", "base"), (23, 16, "root port number", "new"), (15, 0, "max exit latency", "gray")], h=30, label="dw1")
    d.bits(120, 390, 840, 32, [(31, 22, "interrupter", "gray"), (21, 18, "", "gray", 2), (17, 16, "TTT", "base", 3), (15, 8, "TT port", "chg"), (7, 0, "TT hub slot", "chg")], h=30, label="dw2")
    return d.svg("contexts")


def lifecycle():
    d = D(1000, 200, "The life of one device (slot states)")
    x = 15
    for i, (s, cmd, k) in enumerate([("connected", "port reset done", "hw"), ("Enabled", "Enable Slot", "base"), ("Addressed", "Address Device", "chg"),
                                     ("Configured", "Configure Endpoint (step-09)", "new"), ("Disabled", "Disable Slot", "del")]):
        d.box(x, 60, 180, 60, s, [cmd], k, size=12)
        if i:
            d.arrow(x - 15, 90, x - 1, 90)
        x += 197
    d.text(500, 160, "A device that isn't a keyboard goes straight from Addressed to Disabled (freedev); the next device gets its slot number again", 11.5)
    return d.svg("slot states")
