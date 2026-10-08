from svg import D


def tree():
    d = D(1000, 470, "The real PC's (barebone's) USB tree, from the 2026-10-07 screen")
    d.box(380, 45, 240, 50, "xHCI 8086:7a60", ["25 ports, PCI 0:20.0"], "hw", size=12)
    for i, (p, idv, what, k) in enumerate([("port 2", "db0:76", "MSI: ignored", "gray"), ("port 3", "5e3:610", "hub (high)", "chg"),
                                           ("port 5", "46d:c092", "mouse: ignored", "gray"), ("port 6", "4d9:a0f8", "keyboard ← types", "new"),
                                           ("port 7", "480:900", "storage: ignored", "gray"), ("port 8", "4e8:4001", "storage: ignored", "gray"), ("port 11", "5e3:608", "hub (high)", "chg")]):
        x = 15 + i * 140
        d.path(f"M500,95 L500,120 L{x + 65},120 L{x + 65},150")
        d.box(x, 152, 130, 70, p, [idv, what], k, size=11.5)
    d.path("M975,222 L975,262 L905,262 L905,288")
    d.box(830, 290, 150, 70, "port 11.1", ["bda:8178", "Wi-Fi: ignored"], "gray", size=11.5)
    d.text(905, 380, "route = 1, depth 1", 10.5, mono=True)
    d.box(15, 290, 780, 160, "Telling the controller where a device behind hubs is (slot context)", [
        "root port: the first controller port on the way (11)",
        "route string: 4 bits per hub, that hub's port number (11.1 → 0x1, 5.3.2 → 0x23)",
        "TT: for a low/full speed device behind a high speed hub, that hub's slot and port",
        "     (the hub's Transaction Translator converts 480 ↔ 12 / 1.5 Mb/s)",
        "the keyboard was on root port 6 directly: no hub, no TT needed"], "white", size=12)
    return d.svg("the real PC's USB tree")


def hubsetup():
    d = D(1000, 220, "Setting up a hub (usbattach's class 9 branch → hub())")
    x = 15
    for i, (t, ls, k) in enumerate([("SET_CONFIGURATION", ["turn the hub on"], "chg"), ("hub descriptor", ["ports, TT think time,", "power-on time"], "chg"),
                                    ("sethub()", ["Configure Endpoint", "Hub = 1, ports"], "new"), ("power each port", ["SET_FEATURE", "PORT_POWER"], "chg"),
                                    ("each port", ["GET_STATUS → reset", "→ speed → usbattach()"], "chg")]):
        d.box(x, 60, 180, 80, t, ls, k, size=12)
        if i:
            d.arrow(x - 18, 100, x - 1, 100)
        x += 198
    d.box(15, 160, 970, 45, "", ["usbattach() calls hub(), and hub() calls usbattach() again (recursion). Hubs behind hubs take the same path, up to 5 deep"], "white", size=12)
    return d.svg("hub setup")


def route():
    d = D(1000, 250, "The route string (slot context dw0 bits 19:0): 4 bits per hub")
    d.bits(150, 60, 760, 20, [(19, 16, "tier-5 hub port", "gray"), (15, 12, "tier 4", "gray"), (11, 8, "tier 3", "gray"), (7, 4, "tier 2: 2", "new"), (3, 0, "tier 1: 3", "new")], h=44, label="route")
    d.text(530, 140, "port 5.3.2 = root port 5 → port 3 of the first hub → port 2 of the second → route 0x23 (the root port is separate, in dw1)", 12)
    d.text(530, 165, "hub() gives each child: route | (p << (4 × depth)), depth + 1. At most 5 hubs deep (MAXDEPTH)", 12)
    d.text(530, 190, "the real PC's Wi-Fi (port 11.1): root port 11, route 0x1", 12, color="#7d3c98")
    return d.svg("route string")


def tt():
    d = D(1000, 280, "The Transaction Translator: a speed converter inside high speed hubs")
    d.box(30, 100, 180, 70, "xHCI", ["talks at 480 Mb/s"], "hw", size=12)
    d.box(300, 70, 280, 130, "high speed hub", ["one TT per port (or per hub)", "", "480 Mb/s ↔ 12 / 1.5 Mb/s", "split transactions"], "chg", size=12)
    d.box(670, 60, 290, 60, "keyboard (full / low speed)", ["ttslot = the hub's slot, ttport = port"], "new", size=12)
    d.box(670, 150, 290, 60, "Wi-Fi (high speed)", ["no TT needed (ttslot = 0)"], "base", size=12)
    d.arrow(210, 135, 298, 135, "480"); d.arrow(580, 110, 668, 90, "12 / 1.5"); d.arrow(580, 160, 668, 180, "480")
    d.text(500, 240, "QEMU's usb-hub is a full speed hub, so no TT is used → this path can only be tested on a real PC", 12)
    return d.svg("TT")


def hubstatus():
    d = D(1000, 230, "Hub port status (GET_STATUS, 4 bytes = wPortChange : wPortStatus)")
    d.bits(120, 60, 840, 0, [(31, 21, "", "gray", 2), (20, 20, "C_RESET", "chg", 2), (19, 17, "", "gray", 1), (16, 16, "C_CONN", "chg", 2), (15, 11, "", "gray", 2),
                            (10, 10, "HS", "base", 2), (9, 9, "LS", "base", 2), (8, 8, "power", "base", 2), (7, 5, "", "gray", 1), (4, 4, "reset", "new", 2), (3, 2, "", "gray", 1), (1, 1, "enable", "new", 2), (0, 0, "conn", "new", 2)], h=44)
    d.text(540, 140, "hub(): connected (bit 0) → SET_FEATURE(PORT_RESET) → wait for C_RESET (bit 20) → check enabled (bit 1)", 12)
    d.text(540, 165, "speed: bit 9 → low, bit 10 → high, neither → full. CLEAR_FEATURE clears the C_ bits (features 16 and 20)", 12)
    return d.svg("hub port status")
