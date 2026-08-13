from Gaudi.Configuration import *
from MAIAConfig.MAIAConfig.Tracking.CKF_tracking import track_truth_cfg

def makeRecoAlgList(the_args):
    '''-------------------------------------------------------------'''
    '''   Add the Reconstruction Algorithms to the Algorithm List   '''
    '''-------------------------------------------------------------'''
    algList = []
    # Event Counter
    from Common.event_counter import event_counter_cfg
    algList.append(event_counter_cfg())

    # Merging
    from Tracking.mergers import mergehits_cfg, mergehitsrelations_cfg
    algList.append(mergehits_cfg(the_args))
    algList.append(mergehitsrelations_cfg(the_args))

    # CKF Tracking
    from Tracking.CKF_tracking import CKFTracker_cfg, deduper_cfg, track_filter_cfg, ActsGeoSvc_cfg
    ActsGeoSvc_cfg(the_args)  # service: configure it, do NOT append to the algorithm list
    algList.append(CKFTracker_cfg(the_args))
    algList.append(deduper_cfg())
    algList.append(track_filter_cfg())

    # Track Performance Monitoring
    if the_args.doTrackPerf:
        from Diagnostics.track_performance import track_truth_cfg
        algList.append(track_truth_cfg(the_args))

    # Pandora PFOs
    from ParticleFlow.pandora import pandoraPFA_cfg, fastJet_cfg
    algList.append(pandoraPFA_cfg(the_args))
    algList.append(fastJet_cfg())

    return algList
