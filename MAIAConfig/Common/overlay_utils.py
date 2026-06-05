'''-------------------------------------------------------------'''
'''  Helpers for resolving digitiser input collections          '''
'''-------------------------------------------------------------'''
# The overlay algorithms rename their output collections, so a digitiser must
# read whichever collection sits at the end of the overlay chain.


def overlay_input(base_name, args):
    """
    Return the input collection list for a digitiser that nominally reads
    `base_name`, accounting for the overlay chain produced upstream:

      * if --doOverlayIP   -> "OverlayIP<base_name>"
      * elif --doOverlayFull -> "Overlay<base_name>"
      * else               -> "<base_name>" (raw simulation collection)

    IP takes precedence because, when both overlays run, the IP step is the
    last in the chain: it reads the BIB output ("Overlay*") and writes
    "OverlayIP*".
    """
    if getattr(args, "doOverlayIP", False):
        return ["OverlayIP" + base_name]
    if getattr(args, "doOverlayFull", False):
        return ["Overlay" + base_name]
    return [base_name]
