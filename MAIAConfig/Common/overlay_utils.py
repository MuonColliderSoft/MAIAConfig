'''-------------------------------------------------------------'''
'''  Helpers for resolving digitiser input collections          '''
'''-------------------------------------------------------------'''
# The overlay renames its output collections, so a digitiser must read the
# overlay output rather than the raw simulation collection when it ran.

# Prefix the overlay puts on its output collections. Overlay/overlay.py builds
# its output collection names from this, so the two cannot drift apart.
OUTPUT_PREFIX = "Overlay"


def overlay_input(base_name, args):
    """
    Return the input collection list for a digitiser that nominally reads
    `base_name`, accounting for the overlay run upstream:

      * if --doOverlayFull and/or --doOverlayIP -> "Overlay<base_name>"
      * else                                    -> "<base_name>" (raw simulation)

    A single overlay instance handles every enabled background (see
    Overlay/overlay.py), so there is one output prefix regardless of which
    combination of backgrounds is switched on.
    """
    if getattr(args, "doOverlayFull", False) or getattr(args, "doOverlayIP", False):
        return [OUTPUT_PREFIX + base_name]
    return [base_name]
