from GaudiKernel.Constants import INFO, WARNING

def makeDigiAlgList(the_args):
    '''-------------------------------------------------------------'''
    '''    Add the Digitization Algorithms to the Algorithm List    '''
    '''-------------------------------------------------------------'''
    algList = []
    # Event Counter
    from Common.event_counter import event_counter_cfg
    algList.append(event_counter_cfg())

    # Overlay. A single instance overlays whichever backgrounds are enabled --
    # beam-induced background (--doOverlayFull) and/or incoherent pairs
    # (--doOverlayIP) -- as independent background groups on the raw simulation
    # collections, writing the "Overlay*" collections the digitisers pick up via
    # Common.overlay_utils.overlay_input.
    if the_args.doOverlayFull or the_args.doOverlayIP:
        from Overlay.overlay import overlay_cfg
        algList.append(overlay_cfg(the_args))

    # Tracker Digitization. Each subdetector runs either the parametric
    # smearing or, the realistic charge-transport digitisation
    if the_args.doRealisticDigiVertex:
        from TrackerDigi.realistic_vertex import VXDBarrel_cfg, VXDEndcap_cfg
    else:
        from TrackerDigi.tracking_vertex import VXDBarrel_cfg, VXDEndcap_cfg
    if the_args.doRealisticDigiInner:
        from TrackerDigi.realistic_inner import ITBarrel_cfg, ITEndcap_cfg
    else:
        from TrackerDigi.tracking_inner import ITBarrel_cfg, ITEndcap_cfg
    if the_args.doRealisticDigiOuter:
        from TrackerDigi.realistic_outer import OTBarrel_cfg, OTEndcap_cfg
    else:
        from TrackerDigi.tracking_outer import OTBarrel_cfg, OTEndcap_cfg
    algList.append(VXDBarrel_cfg(the_args))
    algList.append(VXDEndcap_cfg(the_args))
    algList.append(ITBarrel_cfg(the_args))
    algList.append(ITEndcap_cfg(the_args))
    algList.append(OTBarrel_cfg(the_args))
    algList.append(OTEndcap_cfg(the_args))

    # Tracker Hit Coning (BIB cleaning). When enabled the merger downstream reads
    # the "...Coned" collections produced here (see Tracking/mergers.py).
    if the_args.doTrackerConing:
        from TrackerDigi.coning import tracker_coner_cfgs
        algList += tracker_coner_cfgs(the_args)

    # EM, Hadronic Calorimeter Digitization
    from CaloDigi.calorimetry_EM import ECalBarrelDigi_cfg, ECalBarrelReco_cfg
    from CaloDigi.calorimetry_EM import ECalEndcapDigi_cfg, ECalEndcapReco_cfg
    algList.append(ECalBarrelDigi_cfg(the_args))
    algList.append(ECalBarrelReco_cfg())
    algList.append(ECalEndcapDigi_cfg(the_args))
    algList.append(ECalEndcapReco_cfg())
    from CaloDigi.calorimetry_HAD import HCalBarrelDigi_cfg, HCalBarrelReco_cfg
    from CaloDigi.calorimetry_HAD import HCalEndcapDigi_cfg, HCalEndcapReco_cfg
    algList.append(HCalBarrelDigi_cfg(the_args))
    algList.append(HCalBarrelReco_cfg())
    algList.append(HCalEndcapDigi_cfg(the_args))
    algList.append(HCalEndcapReco_cfg())

    # Calorimeter Hit Coning (optional) + BIB Selection, mirroring steer_reco.py:
    # each region is coned around the signal MC particles when --doCaloConing is
    # set, and then thresholded, producing the "...Sel" collections that Pandora
    # consumes. Without the coning the selector reads the reconstructed hits.
    from CaloDigi.calo_coning import calo_coner_cfgs, calo_selector_cfgs
    if the_args.doCaloConing:
        algList += calo_coner_cfgs(the_args)
    algList += calo_selector_cfgs(the_args)

    # Muon Calorimeter Digitization
    from CaloDigi.calorimetry_MU import MuonBarrelDigi_cfg, MuonEndcapDigi_cfg
    algList.append(MuonBarrelDigi_cfg(the_args))
    algList.append(MuonEndcapDigi_cfg(the_args))

    # Vertex Filtering
    if the_args.doFilterDL:
        from Tracking.filterDL_vertex import filterDL_vertexBarrel_cfg, filterDL_vertexEndcap_cfg
        algList.append(filterDL_vertexBarrel_cfg())
        algList.append(filterDL_vertexEndcap_cfg())

    return algList
