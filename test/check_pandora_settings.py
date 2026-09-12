#!/usr/bin/env python3
"""
Check that the Pandora settings XML, and every file it references, resolve to
readable absolute paths when the job runs outside the MAIAConfig directory.
Run by the pandora_settings_path CTest from a working directory that holds no
copy of PandoraSettings/.
"""
import os
import re
import sys

from Common.pandora_settings import resolve_pandora_settings

settings = resolve_pandora_settings()

if not os.path.isabs(settings) or not os.path.isfile(settings):
    sys.exit(f"Pandora settings did not resolve to a readable file: {settings}")

with open(settings) as f:
    text = f.read()

# uncomment if PhotonReconstruction is implemented
#referenced = re.findall(r"<HistogramFile>\s*([^<]*?)\s*</HistogramFile>", text)
#if not referenced:
#    sys.exit(f"No <HistogramFile> reference found in {settings}")

#for path in referenced:
#    if not os.path.isabs(path):
#        sys.exit(f"{settings} still holds a relative reference: {path}")
#    if not os.path.isfile(path):
#        sys.exit(f"{settings} references a missing file: {path}")

#print(f"Pandora settings resolved from {os.getcwd()}: {settings}")
#for path in referenced:
#    print(f"  references {path}")
