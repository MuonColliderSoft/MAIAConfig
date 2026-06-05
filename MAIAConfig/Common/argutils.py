'''-------------------------------------------------------------'''
'''  Argument-parser helpers shared across the MAIA steering     '''
'''-------------------------------------------------------------'''
import argparse


def add_argument_once(parser, *args, **kwargs):
    """
    Like ``parser.add_argument`` but a no-op when the option string is already
    registered.

    This lets the digi and reco argument parsers both declare a shared option
    (e.g. --DD4hepXMLFile) so that they can be combined in a single job
    (digi_reco_steer.py) without raising an argparse "conflicting option
    string" error.
    """
    try:
        return parser.add_argument(*args, **kwargs)
    except argparse.ArgumentError:
        return None
