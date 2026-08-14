# MAIAConfig

[![MuColl build and test](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/mucoll-ci.yml/badge.svg)](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/mucoll-ci.yml)
[![pre-commit](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/pre-commit.yaml)
[![downstream-build](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/downstream-build.yaml/badge.svg)](https://github.com/MuonColliderSoft/MAIAConfig/actions/workflows/downstream-build.yaml)

Package for key4hep configuration files related to the MAIA detector concept.

The configuration scripts are meant to be used together with
[mucoll-benchmarks](https://github.com/MuonColliderSoft/mucoll-benchmarks)
to evaluate the detector performance.

## Layout

All steering files and components live under [MAIAConfig/](MAIAConfig), grouped by
domain (following the CLDConfig convention):

- `digi_steer.py` / `reco_steer.py` — the digitisation and reconstruction entry
  points (run with `k4run`).
- `digi_reco_steer.py` — combined entry point that runs digitisation and
  reconstruction in a single `k4run` job (no intermediate digi file).
- `digiAlgList.py` / `recoAlgList.py` — assemble the per-step algorithm lists.
- `digi_args.py` / `reco_args.py` — command-line argument parsers.
- `Common/` — shared helpers used by every steering macro: `steering.py`
  (service + ApplicationMgr wiring), `muc_mt.py` (multi-threading),
  `muc_services.py` (services), `event_counter.py`, `calo_thresholds.py`
  (locates the BIB calorimeter threshold maps).
- `CaloDigi/` — ECal, HCal and Muon calorimeter digitisation/reconstruction,
  plus calorimeter cone filtering and BIB hit selection (`calo_coning.py`).
- `TrackerDigi/` — tracker digitisation (vertex/inner/outer) and tracker-hit
  cone filtering (`coning.py`).
- `Tracking/` — hit merging, CKF track reconstruction, and double-layer filtering.
- `Overlay/` — beam-induced-background (`overlay_BIB.py`) and incoherent-pair
  (`overlay_IP.py`) overlay.
- `ParticleFlow/` — Pandora PFA and jet clustering.
- `Diagnostics/` — tracking performance monitoring.
- `PandoraSettings/` — Pandora steering and likelihood data XMLs. These are
  located automatically, so reconstruction can be run from any directory; use
  `--pandoraSettings` (or `MAIA_PANDORA_SETTINGS_DIR`) to point at your own.

## Usage

The detector geometry is taken from an environment variable (with a
command-line override available: `--DD4hepXMLFile`).

To run the chain from inside the `MAIAConfig/` directory:

```bash
# 1. Simulation (DD4hep) -> sim_output.edm4hep.root
ddsim --compactFile $k4geo_DIR/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml  -G -N 10 \
      --gun.particle mu- --gun.distribution uniform \
      --outputFile sim_output.edm4hep.root

# 2. Digitisation -> digi_output.edm4hep.root
k4run digi_steer.py

# 3. Reconstruction -> reco_output.edm4hep.root
k4run reco_steer.py
```

Alternatively, run digitisation and reconstruction together in one job
(reads `sim_output.edm4hep.root`, writes `digireco_output.edm4hep.root`):

```bash
k4run digi_reco_steer.py
```

### Choosing the input and output files

Each macro reads and writes EDM4hep files with the defaults below, which can be
overridden on the command line with `--inputFiles` (one or more files),
`--outputFile`, and `--histoFile` (ROOT histogram output):

| Macro | Default input | Default output |
|-------|---------------|----------------|
| `digi_steer.py` | `sim_output.edm4hep.root` | `digi_output.edm4hep.root` |
| `reco_steer.py` | `digi_output.edm4hep.root` | `reco_output.edm4hep.root` |
| `digi_reco_steer.py` | `sim_output.edm4hep.root` | `digireco_output.edm4hep.root` |

```bash
# pick the input and output explicitly
k4run reco_steer.py --inputFiles my_digi.edm4hep.root --outputFile my_reco.edm4hep.root

# multiple input files are merged
k4run digi_steer.py --inputFiles sim_0.edm4hep.root sim_1.edm4hep.root
```

Use the k4run built-in `-n N` (`--num-events`) to limit the number of events
(the macros otherwise default to 10).

`k4run --help digi_steer.py` (or `reco_steer.py`) lists the available options.
The full set is:

| Option | Step | Default | Description |
|--------|------|---------|-------------|
| `--DD4hepXMLFile` | both | `$k4geo_DIR/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml` | Compact detector description to use (overrides the geometry default). |
| `--inputFiles` | both | per macro (see above) | Input EDM4hep file(s) to read; accepts several files. |
| `--outputFile` | both | per macro (see above) | Output EDM4hep file to write. |
| `--histoFile` | both | per macro | Output ROOT file for the histograms. |
| `--doOverlayFull` | digi + reco | `False` | Overlay beam-induced background (BIB). In the reco step it only acts as a flag: when set, all tracker and calorimeter hit collections are dropped from the reconstruction output (see below). |
| `--OverlayFullPathToMuPlus` | digi | `/path/to/muplus/` | Directory of the μ⁺ BIB overlay files (used with `--doOverlayFull`). |
| `--OverlayFullPathToMuMinus` | digi | `/path/to/muminus/` | Directory of the μ⁻ BIB overlay files (used with `--doOverlayFull`). |
| `--OverlayFullNumberBackground` | digi | `1667` | Number of BIB background files overlaid (used with `--doOverlayFull`). |
| `--doOverlayIP` | digi + reco | `False` | Overlay incoherent pairs. When both overlays are enabled they are chained (BIB then IP) before digitisation. In the reco step it only acts as a flag: when set, all tracker and calorimeter hit collections are dropped from the reconstruction output (see below). |
| `--OverlayIPBackgroundFileNames` | digi | `[/path/to/pairs.slcio]` | Incoherent-pair overlay input file(s) (used with `--doOverlayIP`). |
| `--doFilterDL` | digi | `False` | Double-layer hit filtering in the vertex detector. |
| `--doTrackerConing` | digi + reco | `False` | Cone-filter the tracker hits around the signal MC particles (BIB cleaning). When enabled, the digi step writes the `…Coned` hit collections and the merger reads them before tracking. |
| `--RandSeed` | digi | `42` | Random seed for the digitisation smearing. |
| `--doTrackPerf` | reco | `False` | Run the tracking performance monitoring. |
| `--keepEverything` | reco | `False` | Write every collection to the reconstruction output, overriding the hit dropping that `--doOverlayFull`/`--doOverlayIP` would otherwise trigger (see below). |
| `--TrackingThreads` | reco | `1` | Internal thread count of the CKF tracking and truth-matching algorithms (independent of `--numThreads`). |
| `--findGNNTracks` | reco | `False` | Additionally run the GNN track finder and seed a second CKF pass with its candidates. Runs alongside the standard CKF chain, which is unaffected; the results go to the separate `GNN…` collections (see below). |
| `--modelBase` | reco | `$MODEL_DIR` | Directory holding the GNN ONNX models (used with `--findGNNTracks`). |
| `--device` | reco | `cpu` | Device for the GNN pipeline: `cpu` or `cuda` (optionally `cuda:<index>`). The default image ships a CPU-only onnxruntime, so `cuda` needs a CUDA-enabled build. |
| `--numThreads` | both | `1` | Number of threads for the Gaudi event loop. `1` runs serially; any value `> 1` enables the multi-threaded Gaudi Hive event loop with that many threads (scheduler + event slots); `0` auto-detects a sensible count from the CPU count. |

### GNN track finding

`--findGNNTracks` runs the GNN track finder *in addition to* the standard CKF
chain rather than in place of it, so a single job produces both and they can be
compared directly. The hits are sorted by φ and the GNN turns them into track
candidates, which are then taken down two paths — one seeding a CKF pass, one
straight from the GNN — each deduped, filtered and (with `--doTrackPerf`)
truth-matched exactly like the standard chain:

```
MergedTrackerHits -> MergedTrackerHitsSortedByPhi -> GNNTrackCandidates
   seeded: -> GNNAllTracks       -> GNNDedupedTracks       -> GNNSiTracks
           (+ GNNSeededTracks, GNNSiTrackRelations)
   direct: -> GNNDirectDedupedTracks -> GNNDirectSiTracks
           (+ GNNDirectSiTrackRelations)
```

The seeded path measures what the CKF makes of the GNN candidates; the direct
path measures what the GNN finds on its own. The standard chain keeps writing
`AllTracks` / `DedupedTracks` / `SiTracks` and is unchanged whether or not the
flag is set. The models are picked up from `--modelBase`:

```bash
k4run reco_steer.py --findGNNTracks --modelBase /path/to/onnx_files
```

Both GNN paths use the same filter cuts as the standard chain, so the three are
directly comparable. Note that those cuts are tuned for CKF output — in
particular `NHitsTotal = 7`, whereas the GNN's own `MinHitsPerTrack` is 3 — so
raw candidates that the CKF would have extended are rejected on the direct path.
Loosen it for that instance alone when studying GNN-only efficiency:

```bash
k4run reco_steer.py --findGNNTracks --modelBase /path/to/onnx_files \
      --GNNDirectFilterer.NHitsTotal 3
```

### Hit collections in the overlay output

Running with background (`--doOverlayFull` and/or `--doOverlayIP`) makes the hit
collections dominate the output file, so `reco_steer.py` drops all of them from
the reconstruction output when either flag is set: the tracker hits
(`drop_tracker_hits`, i.e. `SimTrackerHit`, `TrackerHitPlane`, `TrackerHit3D`)
and the calorimeter hits (`drop_calorimeter_hits`, i.e. `SimCalorimeterHit`,
`CaloHitContribution`, `CalorimeterHit`, which also covers the muon system),
together with the corresponding hit ↔ simulated-hit link collections. The
selection is done by collection *type* through the `IOSvc` keep/drop switch, so
it also covers the collections produced during reconstruction (e.g.
`MergedTrackerHits`).

The reconstructed objects — tracks, Pandora clusters, PFOs, jets, vertices,
`MCParticles` and the track ↔ MC-particle links — are kept, but any reference
they hold into a dropped hit collection (`Track::trackerHits`,
`Cluster::hits`, …) no longer resolves in the output file.

Pass `--keepEverything` to switch the dropping off and write the full event
even with an overlay enabled:

```bash
k4run reco_steer.py --doOverlayFull --keepEverything
```

### BIB hit cleaning

Mirroring the Marlin `steer_reco.py` workflow, once the calorimeter hits are
reconstructed (in the digitisation step) they are always cone-filtered
(`CaloConer`) and then thresholded in energy and time (`CaloHitSelector`),
producing the `…Sel` collections that Pandora consumes during reconstruction.
The ECAL selector reads its per-`(theta, layer)` threshold
maps from the `MyBIBUtils` ROOT files shipped with the software stack; set
`MUCOLL_CALO_THRESHOLDS_DIR` to point at the directory holding those maps if they
cannot be found automatically. Tracker-hit coning is the optional `FilterConeHits`
counterpart, enabled with `--doTrackerConing`.
