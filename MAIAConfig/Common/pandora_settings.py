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
import atexit
import os
import re
import tempfile

# Relative file references inside the settings XML that have to be made
# absolute. Only <HistogramFile> (the likelihood data) is used today; the tuple
# is here so that further tags can be added without touching the logic below.
_PATH_TAGS = ("HistogramFile",)


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


def resolve_pandora_settings(name="PandoraSettingsDefault.xml"):
    """
    Return an absolute path to the Pandora settings XML ``name``, with the
    relative file references it contains rewritten to absolute paths.

    ``name`` may also be an absolute path or a path relative to the current
    working directory (e.g. a user-tuned settings file passed on the command
    line), in which case that file is used instead of the one shipped here.
    Raises FileNotFoundError if the settings file cannot be located.
    """
    settings = _find_settings(name)
    settings_dir = os.path.dirname(settings)

    with open(settings) as f:
        text = f.read()

    patched = _absolutise(text, settings_dir)
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
    atexit.register(_remove_quietly, tmp)
    return tmp


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
