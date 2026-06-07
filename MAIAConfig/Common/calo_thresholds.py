'''-------------------------------------------------------------'''
'''  Locate the BIB calorimeter energy-threshold ROOT files      '''
'''-------------------------------------------------------------'''
# The CaloHitSelector reads per-(theta, layer) energy-threshold maps from ROOT
# files shipped with the MyBIBUtils package (ECAL_Thresholds_<E>.root etc.).
# This helper finds them inside the installed software stack, mirroring the
# findCaloThresholds logic of the Marlin steer_reco.py.
import os
import glob

# MAIA_v0 is the 10 TeV detector, so the 10 TeV threshold maps are the default.
DEFAULT_ENERGY = "10TeV"


def find_calo_thresholds(detector, energy=DEFAULT_ENERGY):
    """
    Return the absolute path to the ``<detector>_Thresholds_<energy>.root`` file
    (``detector`` is "ECAL" or "HCAL"). Set the MUCOLL_CALO_THRESHOLDS_DIR
    environment variable to override the search directory. Raises
    FileNotFoundError if the file cannot be located.
    """
    fname = f"{detector}_Thresholds_{energy}.root"
    candidates = []

    # 1) Explicit override.
    override = os.environ.get("MUCOLL_CALO_THRESHOLDS_DIR")
    if override:
        candidates.append(os.path.join(override, fname))

    # 2) MyBIBUtils ships the maps under <prefix>/share/MyBIBUtils/data/. Locate
    #    the package prefix from the entry it adds to ROOT_INCLUDE_PATH.
    for inc in os.environ.get("ROOT_INCLUDE_PATH", "").split(os.pathsep):
        if "mybibutils" in inc.lower():
            candidates.append(os.path.join(os.path.dirname(inc), "share", "MyBIBUtils", "data", fname))

    # 3) Fall back to globbing the spack architecture directory of the stack.
    stack = os.environ.get("MUCOLL_STACK", "")
    if stack:
        arch_dir = os.path.dirname(os.path.dirname(stack))
        candidates += glob.glob(os.path.join(arch_dir, "mybibutils-*", "share", "MyBIBUtils", "data", fname))

    for path in candidates:
        if path and os.path.isfile(path):
            return path

    raise FileNotFoundError(
        f"Could not locate {fname}; set MUCOLL_CALO_THRESHOLDS_DIR to the "
        "directory containing the MyBIBUtils threshold maps."
    )
