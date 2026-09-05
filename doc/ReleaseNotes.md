# MAIAConfig Release Notes

## Unreleased

Initial set of key4hep configuration scripts to run digitisation and
reconstruction of the MAIA detector concept. The configuration was imported from
[mucoll-benchmarks](https://github.com/MuonColliderSoft/mucoll-benchmarks) and
reorganised to follow, as closely as possible, the layout of
[CLDConfig](https://github.com/key4hep/CLDConfig/tree/main/CLDConfig).

### Steering and structure

- Added the digitisation and reconstruction entry points `digi_steer.py` and
  `reco_steer.py`, driven by `digiAlgList.py` / `recoAlgList.py` and the
  `digi_args.py` / `reco_args.py` argument parsers.
- Added `digi_reco_steer.py`, a combined entry point that runs digitisation and
  reconstruction in a single `k4run` job (the intermediate digi file is kept in
  memory rather than written to disk).
- Factored the service / `ApplicationMgr` boilerplate shared by all three
  steering macros into `Common/steering.py` (`build_application`,
  `merge_alg_lists`), reducing the steering files to thin wrappers.
- The input/output files can be selected on the command line with
  `--inputFiles` (one or more files), `--outputFile` and `--histoFile`,
  defaulting to the per-macro file names.
- Grouped the shared helpers under `Common/` (`steering.py`, `muc_mt.py`,
  `muc_services.py`, `event_counter.py`, `argutils.py`, `overlay_utils.py`).
- Organised the algorithms into CLD-style domain folders:
  - `TrackerDigi/` — tracker digitisation (vertex / inner / outer).
  - `Tracking/` — hit merging, CKF track reconstruction and double-layer filtering.
  - `CaloDigi/` — ECal, HCal and Muon calorimeter digitisation/reconstruction.
  - `Overlay/` — background overlay (beam-induced background, incoherent pairs).
  - `ParticleFlow/` — Pandora PFA and jet clustering.
  - `Diagnostics/` — tracking performance monitoring.
  - `PandoraSettings/` — Pandora steering and likelihood-data XMLs.

### Overlay

- Added the incoherent-pair (IP) overlay, the fully Gaudi-native equivalent of
  the Marlin `OverlayTimingGeneric` processor, gated by `--doOverlayIP` and
  reading the EDM4hep pair files given with `--OverlayIPBackgroundFileNames`.
- Beam-induced background and incoherent pairs are overlaid by a *single*
  `OverlayTimingRandomMix` instance (`Overlay/overlay.py`), one background group
  per source, writing the `Overlay*` collections the digitisers consume.
  Two chained overlay instances do not work: the second looks its background
  collections up in the pair files under the *output* names of the first, which
  do not exist there, and it indexes the signal `MCParticles` collection with the
  unset particle references the first leaves on the background calorimeter
  contributions — an out-of-bounds read that segfaults.
- Because the algorithm decides from the first entry of its file list whether the
  whole list names files or directories, `--OverlayIPBackgroundFileNames` paths
  are folded into the directories that contain them when `--doOverlayFull` is
  enabled as well; on its own `--doOverlayIP` uses exactly the files listed.
- Centralised the digitiser input-collection selection in
  `Common/overlay_utils.overlay_input` (`Overlay*` with either overlay enabled,
  the raw collections otherwise), used by all tracker and calorimeter digitisers.
- The Yoke (muon) collections are currently **not** overlaid: `DDSimpleMuonDigi`
  resolves its input cellID encoding at `initialize()`, which is not available
  for overlay-produced collections. The muon digitisers therefore read the base
  `Yoke*` collections. See the `TODO` in `Overlay/overlay.py` for re-enabling it.
- Renamed `overlay_full.py` to `Overlay/overlay.py`.

### Tracker digitisation

- Added the realistic (charge-transport) tracker digitisation as an option next
  to the parametric smearing: `TrackerDigi/realistic_{vertex,inner,outer}.py`
  configure one `MuonCVXDDigitiser` per subdetector region, gated by the new
  `--doRealisticDigiVertex`, `--doRealisticDigiInner` and `--doRealisticDigiOuter`
  flags (each subdetector can be switched independently).
- The realistic digitisers write the same hit and hit <-> sim-hit link
  collections as the `DDPlanarDigi` ones they replace (`VXDBarrelHits`,
  `VXDBarrelHitsRelations`, ...), so they drop into the existing chain: coning,
  double-layer filtering, hit merging and tracking are unchanged. They also
  produce the local-frame sim hits and raw-hit links, which nothing downstream
  reads. Unlike `DDPlanarDigi`, `MuonCVXDDigitiser` applies no time window.

### Beam-induced-background hit cleaning

- Scheduled the Gaudi-native BIB-cleaning algorithms (from k4Reco) to mimic the
  Marlin `steer_reco.py` workflow:
  - `TrackerDigi/coning.py` — one `FilterConeHits` per tracker subdetector,
    keeping the digitised hits inside a cone around the signal MC particles.
    Gated by `--doTrackerConing`; when enabled the digitisation step writes the
    `…Coned` collections and the hit merger reads them before tracking.
  - `CaloDigi/calo_coning.py` — `CaloConer` (cone filtering) followed by
    `CaloHitSelector` (energy + time thresholding) for each ECal/HCal region.
    The coning is gated by `--doCaloConing` with the cone half-opening angle set
    by `--caloConeWidth` (default 0.6 rad); the selectors always run after
    calorimeter reconstruction, reading the `…Coned` collections when the coning
    is enabled and the reconstructed hits otherwise, and produce the `…Sel`
    collections that Pandora now consumes.
  - `Common/calo_thresholds.py` — locates the `MyBIBUtils` per-`(theta, layer)`
    threshold ROOT files in the software stack (override with
    `MUCOLL_CALO_THRESHOLDS_DIR`). The ECal selector uses these maps; the HCal
    selector uses a flat threshold.

### Multi-threading and arguments

- Replaced the `--useMT` flag with a `--numThreads` knob controlling the Gaudi
  event loop: `1` (default) runs serially, any value `> 1` enables the
  multi-threaded Gaudi Hive event loop with that many threads, and `0`
  auto-detects from the CPU count.
- The tracking algorithms (CKF tracking and truth matching) take their internal
  thread count from a separate `--TrackingThreads` option (default `1`),
  independent of the Gaudi event-loop `--numThreads` setting.
- `build_application` now defaults to `evt_max=-1`, so a steering macro run
  without `k4run -n` processes every event in the input file instead of the
  first 10. `-n` continues to override it.

### MAIA-specific cleanups

- Removed the `DetectorSchema` branching: the CKF tracking now always uses the
  MAIA `CKFTrackingAlg`. Dropped the now-unused `--DetectorSchema`, `--MatFile`,
  `--TGeoFile` and `--TGeoDescFile` arguments.
- Removed the ECal plug and HCal ring digitisation steps and their downstream
  use (not present in MAIA).
- Renamed the Pandora settings folder `PandoraSettingsMAIA/` to `PandoraSettings/`.

### Continuous integration

- Added `mucoll-ci.yml`, building and testing the package inside the
  `ghcr.io/muoncollidersoft/mucoll-sim-ubuntu24:main` image (modelled on the
  k4ActsTracking mucoll CI), replacing the key4hep-stack build which cannot
  provide the MuonCollider components or the MAIA geometry.
- Extended `test/CMakeLists.txt` to chain `ddsim -> digi -> reco` plus `--help`
  smoke tests for the steering macros.
- Added CI status badges (MuColl build and test, pre-commit, downstream-build)
  to the README.
