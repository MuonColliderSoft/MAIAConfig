'''-------------------------------------------------------------'''
'''  Locate and load the Pandora theta-energy calibration tables '''
'''-------------------------------------------------------------'''
# The theta-energy calibration is a pair of 2D (theta, energy) scale-factor
# tables produced by pandora-calibration-tools and applied inside Pandora by the
# NonLinearityCorrection plugin, after clustering and before PfoCreation. The
# tables ship with this package (Calibration/) so that a plain
#     k4run reco_steer.py
# applies the calibration the geometry was tuned with, exactly the way
# PandoraSettings/ and the MyBIBUtils calorimeter thresholds already work.
#
# A payload JSON, as written by
#     pandora-calibration-tools/scripts/build_theta_energy_steering_payload.py
# looks like:
#
#   {
#     "ElectromagneticThetaEnergyCorrectionEnabled":        ["true"],
#     "ElectromagneticThetaEnergyCorrectionPluginName":     ["PhotonEMNonLinearity"],
#     "ElectromagneticThetaEnergyCorrectionThetaBinEdges":  ["0", "0.35", ...],
#     "ElectromagneticThetaEnergyCorrectionEnergyBinEdges": ["0", "5", ...],
#     "ElectromagneticThetaEnergyCorrectionScaleFactors":   ["1.021", ...]
#   }
#
# Every value is a list of strings, because the Marlin-era steering fed the
# payload straight into MarlinProcessorWrapper.Parameters, which was
# dict[str, list[str]]. DDPandoraPFANewAlgorithm is a native Gaudi algorithm
# with typed properties, so the values are coerced back to bool / str /
# list-of-float here. Keeping the on-disk format unchanged means the same
# payload file still works with the older Marlin steering.
#
# IMPORTANT: a calibration table is only valid for the flat calorimeter
# constants it was trained against (ECalToEMGeVCalibration,
# ECalToHadGeVCalibrationBarrel/EndCap, HCalToHadGeVCalibration in
# ParticleFlow/pandora.py) and for the hadronic energy-correction plugin chain
# in PandoraSettings/PandoraSettingsDefault.xml. Change either and the tables
# have to be regenerated: the correction would otherwise be applied in a
# different energy basis than the one it was measured in.
import json
import os

# Payloads loaded when --pandoraCalibration is not given. Missing defaults are a
# warning, not an error, so that a checkout without calibration tables still
# reconstructs (uncalibrated) rather than refusing to run.
DEFAULT_PAYLOADS = (
    "ecal_theta_energy_payload.json",
    "hadronic_theta_energy_payload.json",
)

# Values that switch the calibration off rather than naming a payload.
_OFF_VALUES = ("", "none", "off", "no", "false", "0")


def calibration_dir():
    """
    Return the directory holding the Pandora calibration payloads. Set the
    MAIA_PANDORA_CALIBRATION_DIR environment variable to override the copy
    shipped with this package.
    """
    override = os.environ.get("MAIA_PANDORA_CALIBRATION_DIR")
    if override:
        return os.path.abspath(override)

    # Common/ -> MAIAConfig/ -> Calibration/. This holds both in the source tree
    # and in the installed stack, where CMake copies the whole MAIAConfig/
    # directory to <prefix>/share/MAIAConfig.
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "Calibration")


def _candidate_paths(name):
    """Return the paths ``name`` could resolve to, in priority order."""
    if os.path.isabs(name):
        return [name]
    # A path given relative to the run directory wins only if the packaged copy
    # does not provide that name.
    return [os.path.join(calibration_dir(), name), os.path.abspath(name)]


def _find_payload(name, required=True):
    """
    Resolve ``name`` to an existing payload JSON. Returns None instead of
    raising when the payload is one of the shipped defaults and simply is not
    present in this checkout.
    """
    candidates = _candidate_paths(name)

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    if not required:
        return None

    raise FileNotFoundError(
        f"Could not locate the Pandora calibration payload '{name}' (looked in "
        + ", ".join(candidates)
        + "); set MAIA_PANDORA_CALIBRATION_DIR to the directory containing it."
    )


def _coerce(key, values, path):
    """Turn one payload entry into the value type of the Gaudi property."""
    if not isinstance(values, list):
        raise RuntimeError(f"Expected a list for '{key}' in {path}, got {type(values).__name__}")

    if key.endswith("Enabled"):
        if len(values) != 1:
            raise RuntimeError(f"Expected exactly one value for '{key}' in {path}")
        return str(values[0]).strip().lower() in ("1", "true", "yes", "on")

    if key.endswith("PluginName"):
        if len(values) != 1:
            raise RuntimeError(f"Expected exactly one value for '{key}' in {path}")
        return str(values[0])

    try:
        return [float(v) for v in values]
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Non-numeric entry for '{key}' in {path}") from exc


def load_calibration_payloads(names, required=True):
    """
    Read the payload files ``names`` and return them as a dict of
    DDPandoraPFANewAlgorithm properties, ready to splat into the Configurable.
    Later payloads win on key collisions, so an EM and a HAD payload combine.

    With ``required`` False, payloads that are not present are skipped with a
    warning rather than raising: that is the behaviour for the shipped defaults,
    so that a checkout carrying no calibration tables still runs.
    """
    params = {}
    for name in names:
        path = _find_payload(name, required=required)

        if path is None:
            print(
                f"MAIAConfig: WARNING no Pandora calibration payload '{name}' in "
                f"{calibration_dir()}; reconstruction will run without it"
            )
            continue

        with open(path) as f:
            payload = json.load(f)

        if not isinstance(payload, dict):
            raise RuntimeError(f"Expected a dict payload in {path}")

        for key, values in payload.items():
            params[key] = _coerce(key, values, path)

        print(f"MAIAConfig: loaded Pandora calibration payload {path}")

    _check_shapes(params)
    return params


def _check_shapes(params):
    """
    Fail here, in Python, rather than at Pandora initialisation. A scale-factor
    table with the wrong length is the most common way to break a payload.
    """
    for branch in ("Electromagnetic", "Hadronic"):
        prefix = branch + "ThetaEnergyCorrection"
        if not params.get(prefix + "Enabled", False):
            continue

        theta = params.get(prefix + "ThetaBinEdges", [])
        energy = params.get(prefix + "EnergyBinEdges", [])
        scales = params.get(prefix + "ScaleFactors", [])

        if len(theta) < 2 or len(energy) < 2:
            raise RuntimeError(f"{prefix}: need at least two theta and two energy bin edges")
        if any(b <= a for a, b in zip(theta, theta[1:])):
            raise RuntimeError(f"{prefix}ThetaBinEdges must be strictly increasing")
        if any(b <= a for a, b in zip(energy, energy[1:])):
            raise RuntimeError(f"{prefix}EnergyBinEdges must be strictly increasing")

        expected = (len(theta) - 1) * (len(energy) - 1)
        if len(scales) != expected:
            raise RuntimeError(
                f"{prefix}ScaleFactors holds {len(scales)} entries, expected "
                f"{expected} = ({len(theta)} - 1) * ({len(energy)} - 1)"
            )


def pandora_calibration_params(setting=None):
    """
    Return the calibration properties selected by ``setting``:

      None                       the payloads shipped with this package, if any
      "none" / "off" / "" ...    no calibration (Pandora falls back to identity)
      "a.json,b.json"            a comma-separated list of names or paths

    A bare file name is looked up in the calibration directory; an absolute or
    run-directory relative path is used as given. A payload named explicitly and
    not found is an error; a shipped default that is absent is only a warning.
    """
    if setting is None:
        return load_calibration_payloads(list(DEFAULT_PAYLOADS), required=False)

    text = str(setting).strip()
    if text.lower() in _OFF_VALUES:
        print("MAIAConfig: Pandora theta-energy calibration disabled")
        return {}

    names = [n.strip() for n in text.split(",") if n.strip()]
    return load_calibration_payloads(names, required=True)
