from svg import D


def report():
    d = D(1000, 330, "The boot keyboard report, 8 bytes (as received in QEMU)")
    for i, h in enumerate(["modifiers", "reserved", "key 1", "key 2", "key 3", "key 4", "key 5", "key 6"]):
        d.box(250 + i * 72, 50, 70, 30, h, [], "gray" if i == 1 else "chg" if i == 0 else "base", size=11.5, rx=2)
    rows = [("a down", "0 0 4 0 0 0 0 0", "'a'"), ("a up", "0 0 0 0 0 0 0 0", ""), ("Shift down", "2 0 0 0 0 0 0 0", ""),
            ("a down", "2 0 4 0 0 0 0 0", "'A'"), ("a up", "2 0 0 0 0 0 0 0", ""), ("Shift up", "0 0 0 0 0 0 0 0", "")]
    y = 92
    for lab, v, out in rows:
        d.text(240, y + 19, lab, 11.5, anchor="end")
        for i, x in enumerate(v.split()):
            d.box(250 + i * 72, y, 70, 28, "", [x], "new" if x != "0" else "white", mono=True, size=12.5, rx=2)
        if out:
            d.text(840, y + 19, "→ consoleintr(" + out + ")", 11.5, anchor="start", color="#1e8449")
        y += 32
    d.text(500, y + 20, "a new key = in this report but not in the last one (prev).  Modifier bits: 1 left Ctrl, 2 left Shift, 0x10 right Ctrl, 0x20 right Shift", 11.5)
    return d.svg("keyboard report")


def poll():
    d = D(1000, 250, "An interrupt endpoint is not a CPU interrupt: the controller asks at a fixed interval")
    d.text(20, 60, "controller ↔ keyboard", 12, True, "start", "#2c3e50")
    for i in range(12):
        hit = i in (4, 9)
        d.box(170 + i * 67, 45, 60, 26, "", ["DATA" if hit else "NAK"], "new" if hit else "gray", size=11, rx=2)
    d.text(170, 92, "every 8 ms (QEMU's keyboard: bInterval 7 → 2^6 × 125 µs)", 10.5, anchor="start")
    d.text(20, 140, "CPU", 12, True, "start", "#2c3e50")
    for i in (4, 9):
        x = 170 + i * 67
        d.arrow(x + 30, 72, x + 30, 118, dash=True)
        d.box(x - 30, 120, 120, 40, "", ["transfer event →", "report, queuein()"], "chg", size=10.5, rx=3)
    d.box(20, 180, 960, 50, "", ["queuein(): one Normal TRB (8-byte buffer) + doorbell. Until a key changes the CPU does nothing; on an event it handles the report and calls queuein() again"], "white", size=12)
    return d.svg("interrupt endpoint")


def dci():
    d = D(1000, 230, "Device context index (DCI): set by the endpoint number and direction")
    x = 40
    for n, what, k in [("0", "slot", "gray"), ("1", "EP0 (both ways)", "base"), ("2", "EP1 OUT", "white"), ("3", "EP1 IN", "new"), ("4", "EP2 OUT", "white"),
                       ("5", "EP2 IN", "white"), ("…", "", "white"), ("31", "EP15 IN", "white")]:
        d.box(x, 60, 110, 60, n, [what], k, size=12)
        x += 115
    d.text(500, 150, "DCI = 2 × endpoint number + (1 if IN). QEMU keyboard's interrupt IN endpoint 1 → DCI 3", 12)
    d.text(500, 175, "the doorbell value (db[slot] = kbddci) and the input context's add flag (1 << dci) use this number too", 12)
    d.text(500, 200, "in the input context it is one later: entry 0 is input control, so DCI n is entry n + 1 (ictx(d, dci + 1))", 12)
    return d.svg("DCI")


def keypath():
    d = D(1000, 380, "From a key press to the screen (step-09, polling)")
    for name, x in [("keyboard", 75), ("xHCI controller", 255), ("event ring", 435), ("usbintr → poll", 600), ("usb.cpp", 760), ("console", 905)]:
        d.box(x - 65, 40, 130, 30, name, [], "hw" if x < 500 else "base", size=11.5)
        d.line(x, 70, x, 360, dash=True)
    for a, b, lab, y in [(75, 255, "a down: report [0 0 4 0 …]", 95), (255, 435, "transfer event (Normal TRB done)", 130), (600, 435, "reads TRBs with matching cycle", 165),
                         (600, 760, "usbkbdreport(d, 8)", 200), (760, 905, "consoleintr('a')", 235), (760, 255, "queuein(): ask for the next report + doorbell", 270),
                         (255, 75, "asks every 8 ms (NAK …)", 305)]:
        d.arrow(a, y, b + (4 if b < a else -4), y, color="#1e8449")
        d.text((a + b) / 2, y - 6, lab, 10.5)
    d.text(905, 258, "echo →", 10.5); d.text(905, 273, "screen, serial", 10.5)
    return d.svg("key path")
