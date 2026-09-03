# MAIAConfig Release Notes

## Unreleased

### BIB suppression in Pandora (requires LCContent with isPossibleBIB support)

- Enabled `ShouldExcludeBIBHits` on all `ConeClustering` instances and on
  `MuonReconstruction` in `PandoraSettingsDefault.xml`, and configured the
  `CaloHitPreparation` BIB flagging with per-pseudolayer energy-density cuts
  files (`PandoraSettings/BIBCutsECalBarrel.txt`, `BIBCutsECalEndcap.txt`),
  derived from 3-gaussian fits to the 10 TeV EU24 BIB neighbourhood-energy
  profile at a x2 working point. HCAL cuts and the hit-timing cut are
  supported but left disabled. With a stock LCContent these settings are
  inert (the tags are simply not read).
- The cuts-file tags are path-absolutised by `Common/pandora_settings.py`
  alongside `HistogramFile`, so jobs keep working from any directory.

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
  - `Overlay/` — beam-induced-background and incoherent-pair overlay.
  - `ParticleFlow/` — Pandora PFA and jet clustering.
  - `Diagnostics/` — tracking performance monitoring.
  - `PandoraSettings/` — Pandora steering and likelihood-data XMLs.

### Overlay

- Added the incoherent-pair (IP) overlay (`Overlay/overlay_IP.py`), the fully
  Gaudi-native equivalent of the Marlin `OverlayTimingGeneric` processor, using
  the k4FWCore `OverlayTiming` Configurable (selected explicitly to avoid the
  shadowed k4Reco component of the same name).
- IP overlay is gated by `--doOverlayIP` and chained after the BIB overlay: it
  reads the BIB `Overlay*` collections when `--doOverlayFull` is also set,
  otherwise the raw simulation collections, and writes `OverlayIP*` collections.
- Centralised the digitiser input-collection selection in
  `Common/overlay_utils.overlay_input` (precedence: IP > BIB > raw), used by all
  tracker and calorimeter digitisers.
- The Yoke (muon) collections are currently **not** overlaid: `DDSimpleMuonDigi`
  resolves its input cellID encoding at `initialize()`, which is not available
  for overlay-produced collections. The muon digitisers therefore read the base
  `Yoke*` collections. This applies to both overlays; see the `TODO` in
  `Overlay/overlay_BIB.py` for re-enabling it.
- Renamed `overlay_full.py` to `overlay_BIB.py` for clarity.

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
