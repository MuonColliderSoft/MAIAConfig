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
