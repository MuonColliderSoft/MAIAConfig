'''-------------------------------------------------------------'''
'''  Locate the Pandora settings XML and fix up its paths        '''
'''-------------------------------------------------------------'''
# Pandora's path resolver understands only absolute paths or paths relative to
# the current working directory: it does not resolve a file referenced inside a
# settings XML against the directory of that XML. Without help, running the
# reconstruction from anywhere other than the directory holding PandoraSettings/
# fails, which is why the settings directory had to be copied into the run
# directory by hand (mucoll-benchmarks issue #28).
#
# This helper hands Pandora an absolute path to the settings file, and rewrites
# the relative file references *inside* it to absolute paths in a temporary
# copy, so that reconstruction runs from any working directory.
#
# When the theta-energy calibration is on (--pandoraCalibration, see
# Common/pandora_calibration.py) the same copy also gets the calibration plugins
# added, so a single settings XML serves both modes and any --pandoraSettings
# file picks up the calibration too.
import atexit
import os
import re
import tempfile
import xml.etree.ElementTree as ET

# Relative file references inside the settings XML that have to be made
# absolute. Only <HistogramFile> (the likelihood data) is used today; the tuple
# is here so that further tags can be added without touching the logic below.
_PATH_TAGS = ("HistogramFile",)

# Theta-energy calibration: for each branch, the plugin-list tag and the plugin
# name DDPandoraPFANewAlgorithm registers the table under. The plugin is
# appended to the list, so the hadronic table runs after SoftwareCompensation,
# which is the order it was trained with.
_THETA_ENERGY_PLUGINS = {
    "hadronic": ("HadronicEnergyCorrectionPlugins", "HadronicThetaEnergyBinned"),
    "em": ("ElectromagneticEnergyCorrectionPlugins", "PhotonEMNonLinearity"),
}

# Merging algorithms that compare cluster and track energies. With the hadronic
# table on, they compare tracks with theta-energy corrected cluster energies.
_TRACK_COMPARISON_ALGORITHMS = ("ProximityBasedMerging", "ConeBasedMerging")
_TRACK_COMPARISON_SETTINGS = (
    ("UseThetaEnergyCorrectionForTrackComparison", "true"),
    ("ThetaEnergyCorrectionName", _THETA_ENERGY_PLUGINS["hadronic"][1]),
)


def pandora_settings_dir():
    """
    Return the directory holding the Pandora settings and likelihood XMLs.
    Set the MAIA_PANDORA_SETTINGS_DIR environment variable to override the
    copy shipped with this package.
    """
    override = os.environ.get("MAIA_PANDORA_SETTINGS_DIR")
    if override:
        return os.path.abspath(override)

    # Common/ -> MAIAConfig/ -> PandoraSettings/. This holds both in the source
    # tree and in the installed stack, where CMake copies the whole MAIAConfig/
    # directory to <prefix>/share/MAIAConfig.
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "PandoraSettings")


def resolve_pandora_settings(name="PandoraSettingsDefault.xml", theta_energy_branches=()):
    """
    Return an absolute path to the Pandora settings XML ``name``, with the
    relative file references it contains rewritten to absolute paths.

    ``name`` may also be an absolute path or a path relative to the current
    working directory (e.g. a user-tuned settings file passed on the command
    line), in which case that file is used instead of the one shipped here.
    Raises FileNotFoundError if the settings file cannot be located.

    ``theta_energy_branches`` lists the calibration branches that are on ("em",
    "hadronic"); their plugins are added to the copy handed to Pandora, see
    add_theta_energy_corrections(). That copy is then kept after the job, and
    its path printed, so the settings Pandora actually ran with can be checked.
    """
    settings = _find_settings(name)
    settings_dir = os.path.dirname(settings)

    with open(settings) as f:
        text = f.read()

    patched = text
    if theta_energy_branches:
        patched, changes = add_theta_energy_corrections(patched, theta_energy_branches)

    patched = _absolutise(patched, settings_dir)
    if patched == text:
        # Nothing to rewrite: let Pandora read the file in place.
        return settings

    # A temporary copy keeps the shipped XML untouched (it lives in a read-only
    # install directory once the stack is built) and keeps its relative paths
    # working for anyone still copying PandoraSettings/ into their run
    # directory. mkstemp gives a unique name, so concurrent jobs sharing a
    # /tmp do not overwrite each other's copy.
    fd, tmp = tempfile.mkstemp(prefix="MAIA_PandoraSettings_", suffix=".xml")
    with os.fdopen(fd, "w") as f:
        f.write(patched)

    if theta_energy_branches:
        print(f"MAIAConfig: Pandora settings {settings} patched for the theta-energy calibration:")
        for change in changes or ["nothing to add, the XML already sets everything"]:
            print(f"MAIAConfig:   {change}")
        print(f"MAIAConfig: patched settings kept as {tmp}")
    else:
        atexit.register(_remove_quietly, tmp)
    return tmp


def add_theta_energy_corrections(text, branches):
    """
    Add the theta-energy calibration to the Pandora settings XML ``text`` for
    the given ``branches`` ("em", "hadronic"), and return the new text together
    with a list describing each change made.

    For each branch the calibration plugin is appended to that branch's energy
    correction plugin list (the list is created if the XML has none). For the
    hadronic branch, ProximityBasedMerging and ConeBasedMerging are also told
    to compare tracks with theta-energy corrected cluster energies.

    Anything the XML already sets is left as it is: a plugin already listed is
    not added twice, and an explicit UseThetaEnergyCorrectionForTrackComparison
    (true or false) is respected. If the XML has no ProximityBasedMerging or
    ConeBasedMerging algorithm, this raises rather than leaving the merging
    checks silently uncorrected.
    """
    unknown = set(branches) - set(_THETA_ENERGY_PLUGINS)
    if unknown:
        raise ValueError(f"Unknown theta-energy calibration branches: {sorted(unknown)}")

    # Keep everything before the root element (the leading comment), and the
    # comments inside it, so the patched copy still reads like the original.
    start = re.search(r"<pandora\b", text)
    if start is None:
        raise RuntimeError("Pandora settings XML has no <pandora> root element")
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.fromstring(text[start.start():], parser=parser)

    changes = []
    # Hadronic first, so a newly created EM list lands after the hadronic one.
    for basis in ("hadronic", "em"):
        if basis in branches:
            tag, plugin = _THETA_ENERGY_PLUGINS[basis]
            change = _add_plugin(root, tag, plugin)
            if change:
                changes.append(change)

    if "hadronic" in branches:
        changes.extend(_enable_track_comparison(root))

    return text[:start.start()] + ET.tostring(root, encoding="unicode") + "\n", changes


def _add_plugin(root, tag, plugin):
    """Append ``plugin`` to the plugin list ``tag``; return a description, or None."""
    lists = root.findall(tag)
    if len(lists) > 1:
        raise RuntimeError(f"Pandora settings XML has more than one <{tag}>")

    if lists:
        names = (lists[0].text or "").split()
        if plugin in names:
            return None
        lists[0].text = " ".join(names + [plugin])
        return f"appended {plugin} to <{tag}>"

    # No list yet: create one next to the other energy-correction list if there
    # is one, otherwise at the top of the global settings.
    element = ET.Element(tag)
    element.text = plugin
    children = list(root)
    anchor = next(
        (i for i, child in enumerate(children)
         if child.tag in ("HadronicEnergyCorrectionPlugins", "ElectromagneticEnergyCorrectionPlugins")),
        None,
    )
    if anchor is None:
        element.tail = root.text
        root.insert(0, element)
    else:
        element.tail = children[anchor].tail
        root.insert(anchor + 1, element)
    return f"created <{tag}> with {plugin}"


def _enable_track_comparison(root):
    """Turn on the theta-energy track comparison in the merging algorithms."""
    changes = []
    for algorithm_type in _TRACK_COMPARISON_ALGORITHMS:
        algorithms = [a for a in root.iter("algorithm") if a.get("type") == algorithm_type]
        if not algorithms:
            raise RuntimeError(
                f"The Pandora settings XML has no {algorithm_type} algorithm, so the "
                "theta-energy track comparison cannot be turned on. Add it to the XML, "
                "or update _TRACK_COMPARISON_ALGORITHMS in Common/pandora_settings.py."
            )

        for algorithm in algorithms:
            if algorithm.find(_TRACK_COMPARISON_SETTINGS[0][0]) is not None:
                # Set explicitly in the XML: respect it, and its name.
                continue

            for tag, value in _TRACK_COMPARISON_SETTINGS:
                if algorithm.find(tag) is not None:
                    continue
                _append_child(algorithm, tag, value)
            changes.append(f"set {_TRACK_COMPARISON_SETTINGS[0][0]} in {algorithm_type}")
    return changes


def _append_child(parent, tag, value):
    """Append <tag>value</tag> to ``parent``, following its indentation."""
    element = ET.SubElement(parent, tag)
    element.text = value

    children = list(parent)
    if len(children) == 1:
        # The parent was empty (<algorithm .../>): no indentation to follow.
        return
    previous = children[-2]
    element.tail = previous.tail
    previous.tail = parent.text


def _find_settings(name):
    """Resolve ``name`` to an existing settings file, or raise."""
    candidates = []
    if os.path.isabs(name):
        candidates.append(name)
    else:
        candidates.append(os.path.join(pandora_settings_dir(), name))
        # A path given relative to the run directory wins only if the packaged
        # copy does not provide that name.
        candidates.append(os.path.abspath(name))

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    raise FileNotFoundError(
        f"Could not locate the Pandora settings file '{name}' (looked in "
        + ", ".join(candidates)
        + "); set MAIA_PANDORA_SETTINGS_DIR to the directory containing it."
    )


def _absolutise(text, settings_dir):
    """
    Rewrite the relative paths held by the _PATH_TAGS elements of the settings
    XML ``text`` so that they point inside ``settings_dir``. Absolute paths are
    left alone.
    """
    for tag in _PATH_TAGS:
        pattern = re.compile(rf"(<{tag}>\s*)([^<]*?)(\s*</{tag}>)")

        def _rewrite(match):
            path = match.group(2)
            if not path or os.path.isabs(path):
                return match.group(0)
            # The referenced files live next to the settings XML, so only the
            # file name of the recorded path is meaningful here.
            resolved = os.path.join(settings_dir, os.path.basename(path))
            return match.group(1) + resolved + match.group(3)

        text = pattern.sub(_rewrite, text)

    return text


def _remove_quietly(path):
    try:
        os.remove(path)
    except OSError:
        pass
