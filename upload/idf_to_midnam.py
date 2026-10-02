#!/usr/bin/env python3
"""Convert a MusE .idf MIDI instrument definition into a MIDNAM (.midnam)
patch file plus a companion .middev device descriptor.

MIDNAM structure verified against a real-world Ardour-shipped file
(Yamaha_PSR_S900.midnam) fetched from github.com/Ardour/ardour.
MIDDEV structure verified against DaveSmithInstruments.middev
(github.com/SquishyCat/MIDI-Configs).
"""
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

SRC = "/home/alan/src/casio/Casio_CDP-S360.idf"
MIDNAM_OUT = "/home/alan/src/casio/Casio_CDP-S360.midnam"
MIDDEV_OUT = "/home/alan/src/casio/Casio_CDP-S360.middev"

MANUFACTURER = "Casio"
MODEL = "CDP-S360"

tree = ET.parse(SRC)
root = tree.getroot()
instrument = root.find("MidiInstrument")

groups = []
for pg in instrument.findall("PatchGroup"):
    name = pg.get("name")
    # Drop the trailing " (CATEGORY : N)" — MIDNAM patch bank names are
    # shown as-is in the DAW's patch selector, the category number adds
    # nothing there and the document order already preserves it.
    clean_name = name.split(" (CATEGORY")[0].strip()
    patches = []
    for p in pg.findall("Patch"):
        patches.append({
            "name": p.get("name"),
            "lbank": int(p.get("lbank", "0")),
            "hbank": int(p.get("hbank", "0")),
            "prog": int(p.get("prog", "0")),
            "drum": p.get("drum") == "1",
        })
    groups.append((clean_name, patches))

total_patches = sum(len(p) for _, p in groups)
print(f"Parsed {len(groups)} patch groups, {total_patches} patches total")

# --- Build .midnam ---------------------------------------------------

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<!DOCTYPE MIDINameDocument PUBLIC "-//MIDI Manufacturers Association//DTD MIDINameDocument 1.0//EN" "http://www.midi.org/dtds/MIDINameDocument10.dtd">')
lines.append('<MIDINameDocument>')
lines.append('  <Author>Converted from MusE Casio_CDP-S360.idf</Author>')
lines.append('  <MasterDeviceNames>')
lines.append(f'    <Manufacturer>{escape(MANUFACTURER)}</Manufacturer>')
lines.append(f'    <Model>{escape(MODEL)}</Model>')
lines.append('    <CustomDeviceMode Name="Default">')
lines.append('      <ChannelNameSetAssignments>')
for ch in range(1, 17):
    lines.append(f'        <ChannelNameSetAssign Channel="{ch}" NameSet="Default"/>')
lines.append('      </ChannelNameSetAssignments>')
lines.append('    </CustomDeviceMode>')
lines.append('    <ChannelNameSet Name="Default">')
lines.append('      <AvailableForChannels>')
for ch in range(1, 17):
    lines.append(f'        <AvailableChannel Channel="{ch}" Available="true"/>')
lines.append('      </AvailableForChannels>')

for group_name, patches in groups:
    lines.append(f'      <PatchBank Name="{escape(group_name)}">')
    lines.append('        <PatchNameList>')
    for i, p in enumerate(patches, start=1):
        lines.append(f'          <Patch Number="{i}" Name="{escape(p["name"])}">')
        lines.append('            <PatchMIDICommands>')
        lines.append(f'              <ControlChange Control="0" Value="{p["hbank"]}"/>')
        lines.append(f'              <ControlChange Control="32" Value="{p["lbank"]}"/>')
        lines.append(f'              <ProgramChange Number="{p["prog"]}"/>')
        lines.append('            </PatchMIDICommands>')
        lines.append('          </Patch>')
    lines.append('        </PatchNameList>')
    lines.append('      </PatchBank>')

lines.append('    </ChannelNameSet>')
lines.append('  </MasterDeviceNames>')
lines.append('</MIDINameDocument>')

with open(MIDNAM_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Wrote {MIDNAM_OUT}")

# --- Build .middev -----------------------------------------------------
# InquiryResponse (SysEx Family/Member bytes) deliberately omitted: those
# codes for the CDP-S360 aren't publicly documented in a source I could
# verify, and a wrong value is worse than none (breaks auto-detection
# silently). DeviceID/Receives/Transmits are generic/safe to state.

middev_lines = []
middev_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
middev_lines.append('<!DOCTYPE MIDIDeviceTypes PUBLIC "-//MIDI Manufacturers Association//DTD MIDIDeviceTypes 0.3//EN" "http://www.sonosphere.com/dtds/MIDIDeviceTypes.dtd">')
middev_lines.append('')
middev_lines.append('<MIDIDeviceTypes>')
middev_lines.append(f'\t<MIDIDeviceType Manufacturer="{escape(MANUFACTURER)}" Model="{escape(MODEL)}" SupportsGeneralMIDI="true" SupportsMMC="false" IsSampler="false" IsDrumMachine="false" IsMixer="false" IsEffectUnit="false" >')
middev_lines.append('\t\t<DeviceID Min="1" Max="16" Default="1" Base="1" />')
middev_lines.append('\t\t<Receives MaxChannels="16" MTC="false" Clock="true" Notes="true" ProgramChanges="true" BankSelectMSB="true" BankSelectLSB="true" PanDisruptsStereo="false" />')
middev_lines.append('\t\t<Transmits MaxChannels="16" MTC="false" Clock="true" Notes="true" ProgramChanges="true" BankSelectMSB="true" BankSelectLSB="true" />')
middev_lines.append('\t</MIDIDeviceType>')
middev_lines.append('</MIDIDeviceTypes>')

with open(MIDDEV_OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(middev_lines) + "\n")

print(f"Wrote {MIDDEV_OUT}")
