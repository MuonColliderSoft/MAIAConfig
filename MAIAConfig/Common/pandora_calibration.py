'''-------------------------------------------------------------'''
'''  Locate and load the Pandora theta-energy calibration tables '''
'''-------------------------------------------------------------'''
# The theta-energy calibration is a pair of 2D (theta, energy) scale-factor
# tables produced by pandora-calibration-tools and applied inside Pandora by the
# PhotonEMNonLinearity and HadronicThetaEnergyBinned plugins, after clustering
# and before PfoCreation. The tables ship with this package (Calibration/).
#
# The calibration is opt-in. A plain
#     k4run reco_steer.py
# reconstructs exactly as before. Pass
#     --pandoraCalibration default
# to use the tables shipped in Calibration/, or a comma-separated list of table
# files to use your own.
#
# A table JSON, as written by
#     pandora-calibration-tools/scripts/make_ecal_theta_energy_calibration.py
#     pandora-calibration-tools/scripts/make_hcal_theta_energy_calibration.py
# looks like:
#
#   {
#     "theta_edges":  [0.15, 0.4, ...],
#     "energy_edges": [30.0, 50.0, ...],
#     "scales":       [1.021, ...],
#     "metadata":     {"energy_basis": "em", ...}
#   }
#
# DDPandoraPFANewAlgorithm reads the file itself (ElectromagneticThetaEnergy-
# CorrectionFile / HadronicThetaEnergyCorrectionFile) and checks the table shape
# and energy_basis at initialize(). This module only finds the files, sends each
# one to the right branch by its metadata.energy_basis, and returns the flat
# Pandora constants the tables were trained against.
#
# IMPORTANT: a calibration table is only valid for the flat calorimeter
# constants it was trained against (CALIBRATED_PANDORA_CONSTANTS below) and for
# the hadronic energy-correction plugin chain it runs in (SoftwareCompensation,
# then the table). The plugins are added to the Pandora settings XML at run time
# by Common/pandora_settings.py, whichever XML is used. Those constants replace the
# defaults in ParticleFlow/pandora.py only when the calibration is on, so the
# default reconstruction is unchanged. Change any of them and the tables have to
# be regenerated: the correction would otherwise be applied in a different
# energy basis than the one it was measured in.
import json
import os

# Tables loaded by --pandoraCalibration default.
DEFAULT_TABLES = (
    "ecal_theta_energy_calib.json",
    "hadronic_theta_energy_calib.json",
)

# Values that request the tables shipped in Calibration/.
_DEFAULT_VALUES = ("default", "on", "yes", "true", "1")

# Values that switch the calibration off rather than naming a table.
_OFF_VALUES = ("", "none", "off", "no", "false", "0")

# Which DDPandoraPFANewAlgorithm property each metadata.energy_basis feeds.
_BRANCH_PROPERTY = {
    "em": "ElectromagneticThetaEnergyCorrectionFile",
    "hadronic": "HadronicThetaEnergyCorrectionFile",
}

# Flat Pandora constants each branch's table was trained against. They replace
# the defaults in ParticleFlow/pandora.py only for the branches that are on.
CALIBRATED_PANDORA_CONSTANTS = {
    "em": {
        "ECalToEMGeVCalibration": 1.02373335516,
    },
    "hadronic": {
        "ECalToHadGeVCalibrationBarrel": 1.38,
        "ECalToHadGeVCalibrationEndCap": 1.38,
        "HCalToHadGeVCalibration": 1.25,
        # Software compensation is turned off by setting its upper cluster-energy
        # limit to 0 GeV, so no cluster qualifies for it. The hadronic table was
        # trained on samples reconstructed with soft compensation off, and
        # HadronicThetaEnergyBinned runs after SoftwareCompensation, so the table
        # already absorbs that correction. Turning it back on (the default in
        # ParticleFlow/pandora.py is 2000.) means regenerating the hadronic table.
        "MaxClusterEnergyToApplySoftComp": 0.,
    },
}

# Table metadata keys that record the flat constants used in training, and the
# Pandora constants each one has to match.
_METADATA_CONSTANTS = {
    "ecal_to_em_gev": ("ECalToEMGeVCalibration",),
    "ecal_to_had_gev": ("ECalToHadGeVCalibrationBarrel", "ECalToHadGeVCalibrationEndCap"),
    "hcal_to_had_gev": ("HCalToHadGeVCalibration",),
}


def calibration_dir():
    """
    Return the directory holding the Pandora calibration tables. Set the
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


def _find_table(name):
    """Resolve ``name`` to an existing table JSON."""
    candidates = _candidate_paths(name)

    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)

    raise FileNotFoundError(
        f"Could not locate the Pandora calibration table '{name}' (looked in "
        + ", ".join(candidates)
        + "); set MAIA_PANDORA_CALIBRATION_DIR to the directory containing it."
    )


def _read_metadata(path):
    """Return the metadata block of the table at ``path``."""
    with open(path) as f:
        table = json.load(f)

    if not isinstance(table, dict):
        raise RuntimeError(f"Expected a dict table in {path}")

    metadata = table.get("metadata")
    if not isinstance(metadata, dict) or "energy_basis" not in metadata:
        raise RuntimeError(
            f"{path} has no metadata.energy_basis, so it cannot be assigned to "
            "the EM or hadronic branch"
        )
    return metadata


def _check_constants(basis, metadata, path):
    """
    Fail here, in Python, if the table was trained with different flat constants
    than the ones Pandora will run with.
    """
    constants = CALIBRATED_PANDORA_CONSTANTS[basis]

    for key, properties in _METADATA_CONSTANTS.items():
        trained = metadata.get(key)
        if trained is None:
            continue

        for prop in properties:
            if prop not in constants:
                continue
            used = constants[prop]
            if abs(float(trained) - used) > 1e-6 * max(1.0, abs(used)):
                raise RuntimeError(
                    f"{path} was trained with {key} = {trained}, but the "
                    f"calibration runs Pandora with {prop} = {used}. Regenerate "
                    "the table or update CALIBRATED_PANDORA_CONSTANTS."
                )


def load_calibration_tables(names):
    """
    Resolve the table files ``names`` and return them, together with the flat
    constants their branches were trained against, as a dict of
    DDPandoraPFANewAlgorithm properties.
    """
    params = {}
    for name in names:
        path = _find_table(name)
        metadata = _read_metadata(path)

        basis = str(metadata["energy_basis"]).strip().lower()
        if basis not in _BRANCH_PROPERTY:
            raise RuntimeError(
                f"{path} has energy_basis '{basis}', expected one of "
                + ", ".join(_BRANCH_PROPERTY)
            )

        prop = _BRANCH_PROPERTY[basis]
        if prop in params:
            raise RuntimeError(f"Two '{basis}' tables given: {params[prop]} and {path}")

        _check_constants(basis, metadata, path)

        params[prop] = path
        params.update(CALIBRATED_PANDORA_CONSTANTS[basis])

        print(f"MAIAConfig: loaded Pandora {basis} calibration table {path}")

    return params


def calibration_branches(params):
    """
    Return the branches ("em", "hadronic") that have a table in ``params``, as
    returned by pandora_calibration_params().
    """
    return tuple(basis for basis, prop in _BRANCH_PROPERTY.items() if prop in params)


def pandora_calibration_params(setting=None):
    """
    Return the calibration properties selected by ``setting``:

      None / "none" / "off" ...  no calibration (the default)
      "default"                  the tables shipped in Calibration/
      "a.json,b.json"            a comma-separated list of names or paths

    A bare file name is looked up in the calibration directory; an absolute or
    run-directory relative path is used as given. Each table is sent to the EM
    or hadronic branch by its metadata.energy_basis. A table that is asked for
    and not found is an error.
    """
    if setting is None:
        return {}

    text = str(setting).strip()
    if text.lower() in _OFF_VALUES:
        print("MAIAConfig: Pandora theta-energy calibration disabled")
        return {}

    if text.lower() in _DEFAULT_VALUES:
        names = list(DEFAULT_TABLES)
    else:
        names = [n.strip() for n in text.split(",") if n.strip()]

    return load_calibration_tables(names)
