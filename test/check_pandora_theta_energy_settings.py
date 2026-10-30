#!/usr/bin/env python3
"""
Check that turning on the theta-energy calibration adds its plugins to the
Pandora settings XML, and that the default reconstruction is left untouched.
Run by the pandora_theta_energy_settings CTest.
"""
import os
import sys
import xml.etree.ElementTree as ET

from Common.pandora_settings import (
    add_theta_energy_corrections,
    pandora_settings_dir,
    resolve_pandora_settings,
)

HADRONIC = "HadronicThetaEnergyBinned"
EM = "PhotonEMNonLinearity"
MERGING = ("ProximityBasedMerging", "ConeBasedMerging")


def fail(message):
    sys.exit(f"FAIL: {message}")


def plugins(root, tag):
    element = root.find(tag)
    return (element.text or "").split() if element is not None else []


def merging_settings(root):
    return [
        (a.findtext("UseThetaEnergyCorrectionForTrackComparison"), a.findtext("ThetaEnergyCorrectionName"))
        for a in root.iter("algorithm") if a.get("type") in MERGING
    ]


with open(os.path.join(pandora_settings_dir(), "PandoraSettingsDefault.xml")) as f:
    default = f.read()

# Calibration off: the default XML must carry none of the calibration settings.
root = ET.fromstring(open(resolve_pandora_settings()).read())
if HADRONIC in plugins(root, "HadronicEnergyCorrectionPlugins") or root.find("ElectromagneticEnergyCorrectionPlugins") is not None:
    fail("the default settings name a theta-energy plugin")
if any(use for use, _ in merging_settings(root)):
    fail("the default settings turn on the theta-energy track comparison")

# Both branches on.
text, changes = add_theta_energy_corrections(default, ("em", "hadronic"))
root = ET.fromstring(text)
if plugins(root, "HadronicEnergyCorrectionPlugins") != ["SoftwareCompensation", HADRONIC]:
    fail(f"hadronic plugins are {plugins(root, 'HadronicEnergyCorrectionPlugins')}")
if plugins(root, "ElectromagneticEnergyCorrectionPlugins") != [EM]:
    fail(f"EM plugins are {plugins(root, 'ElectromagneticEnergyCorrectionPlugins')}")
settings = merging_settings(root)
if len(settings) != len(MERGING) or any(s != ("true", HADRONIC) for s in settings):
    fail(f"merging algorithms have {settings}")
# The comments survive, so the kept copy still reads like the original.
if "<!-- PLUGIN REGISTRATION -->" not in text:
    fail("comments were dropped from the patched XML")

# Patching twice changes nothing.
again, more = add_theta_energy_corrections(text, ("em", "hadronic"))
if more or ET.tostring(ET.fromstring(again)) != ET.tostring(root):
    fail(f"patching an already patched XML changed it: {more}")

# EM only: no hadronic plugin and no merging change.
root = ET.fromstring(add_theta_energy_corrections(default, ("em",))[0])
if HADRONIC in plugins(root, "HadronicEnergyCorrectionPlugins") or any(u for u, _ in merging_settings(root)):
    fail("the EM-only calibration touched the hadronic settings")

# An explicit setting in the XML is respected.
explicit = default.replace(
    '<algorithm type = "ConeBasedMerging">',
    '<algorithm type = "ConeBasedMerging">\n<UseThetaEnergyCorrectionForTrackComparison>false</UseThetaEnergyCorrectionForTrackComparison>',
)
root = ET.fromstring(add_theta_energy_corrections(explicit, ("hadronic",))[0])
cone = next(a for a in root.iter("algorithm") if a.get("type") == "ConeBasedMerging")
if cone.findtext("UseThetaEnergyCorrectionForTrackComparison") != "false":
    fail("an explicit UseThetaEnergyCorrectionForTrackComparison was overridden")

# An XML without the merging algorithms fails loudly.
try:
    add_theta_energy_corrections(default.replace("ProximityBasedMerging", "SomethingElse"), ("hadronic",))
except RuntimeError:
    pass
else:
    fail("a missing ProximityBasedMerging did not raise")

# Through resolve_pandora_settings: a kept copy, still with absolute paths.
path = resolve_pandora_settings(theta_energy_branches=("em", "hadronic"))
root = ET.fromstring(open(path).read())
if plugins(root, "HadronicEnergyCorrectionPlugins")[-1:] != [HADRONIC]:
    fail(f"{path} does not name {HADRONIC}")
for histogram in root.iter("HistogramFile"):
    if not os.path.isabs(histogram.text.strip()):
        fail(f"{path} still holds a relative reference: {histogram.text}")
os.remove(path)

print("Pandora theta-energy settings patching OK")
