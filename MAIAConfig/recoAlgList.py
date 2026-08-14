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
    algList.append(mergehits_cfg(the_args))
    algList.append(mergehitsrelations_cfg(the_args))

    # CKF Tracking
    from Tracking.CKF_tracking import CKFTracker_cfg, deduper_cfg, track_filter_cfg, ActsGeoSvc_cfg
    ActsGeoSvc_cfg(the_args)  # service: configure it, do NOT append to the algorithm list
    algList.append(CKFTracker_cfg(the_args))
    algList.append(deduper_cfg())
    algList.append(track_filter_cfg())

    # GNN Tracking. Runs alongside the standard CKF chain above rather than
    # replacing it: the GNN track finder produces candidates that seed a second
    # CKF pass, and the whole branch stays in its own GNN* collections so the
    # two can be compared in the same job.
    if the_args.findGNNTracks:
        from Tracking.CKF_tracking import CKFFromSeeds_cfg
        from Tracking.GNN_tracking import GNNTracker_cfg, HitSorter_cfg
        algList.append(HitSorter_cfg(the_args))
        algList.append(GNNTracker_cfg(the_args))
        algList.append(CKFFromSeeds_cfg(the_args))
        algList.append(deduper_cfg("GNNDeduper", "GNNAllTracks", "GNNDedupedTracks"))
        algList.append(track_filter_cfg("GNNFilterer", "GNNDedupedTracks", "GNNSiTracks"))

    # Track Performance Monitoring
    if the_args.doTrackPerf:
        from Diagnostics.track_performance import track_truth_cfg
        algList.append(track_truth_cfg(the_args))
        if the_args.findGNNTracks:
            algList.append(track_truth_cfg(
                the_args, "GNNTruthMatcher", "GNNSiTracks", "GNNSiTrackRelations"
            ))

    # Pandora PFOs
    from ParticleFlow.pandora import pandoraPFA_cfg, fastJet_cfg
    algList.append(pandoraPFA_cfg(the_args))
    algList.append(fastJet_cfg())

    return algList
