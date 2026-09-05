'''-------------------------------------------------------------'''
'''  Helpers for resolving digitiser input collections          '''
'''-------------------------------------------------------------'''
# The overlay algorithm renames its output collections, so a digitiser must
# read whichever collection sits at the end of the overlay chain.


def overlay_input(base_name, args):
    """
    Return the input collection list for a digitiser that nominally reads
    `base_name`, accounting for the overlay produced upstream:

      * with --doOverlayFull and/or --doOverlayIP -> "Overlay<base_name>"
      * otherwise                                 -> "<base_name>"

    Both background sources are overlaid by the same algorithm (see
    Overlay/overlay.py), so they share the one "Overlay*" set of outputs.
    """
    if getattr(args, "doOverlayFull", False) or getattr(args, "doOverlayIP", False):
        return ["Overlay" + base_name]
    return [base_name]
