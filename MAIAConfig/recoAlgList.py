from Gaudi.Configuration import *

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
    algList.append(mergehits_cfg())
    algList.append(mergehitsrelations_cfg())

    # CKF Tracking
    from Tracking.CKF_tracking import CKFTracker_cfg, deduper_cfg, track_filter_cfg, track_truth_cfg, track_refitter_cfg
    algList.append(CKFTracker_cfg(the_args))
    algList.append(deduper_cfg())
    algList.append(track_filter_cfg())
    algList.append(track_truth_cfg(the_args))
    # algList.append(track_refitter_cfg())

    # Track Performance Monitoring
    if the_args.doTrackPerf:
        from Diagnostics.track_performance import trackPerf_cfg, trackTruth_cfg
        algList.append(trackTruth_cfg())
        algList.append(trackPerf_cfg())

    # Pandora PFOs
    from ParticleFlow.pandora import pandoraPFA_cfg, fastJet_cfg
    algList.append(pandoraPFA_cfg())
    algList.append(fastJet_cfg())

    return algList
