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
- `PandoraSettings/` — Pandora steering and likelihood data XMLs (must be
  present in the directory where reconstruction is run).

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
| `--doOverlayFull` | digi | `False` | Overlay beam-induced background (BIB). |
| `--OverlayFullPathToMuPlus` | digi | `/path/to/muplus/` | Directory of the μ⁺ BIB overlay files (used with `--doOverlayFull`). |
| `--OverlayFullPathToMuMinus` | digi | `/path/to/muminus/` | Directory of the μ⁻ BIB overlay files (used with `--doOverlayFull`). |
| `--OverlayFullNumberBackground` | digi | `812` | Number of BIB background files overlaid (used with `--doOverlayFull`). |
| `--doOverlayIP` | digi | `False` | Overlay incoherent pairs. When both overlays are enabled they are chained (BIB then IP) before digitisation. |
| `--OverlayIPBackgroundFileNames` | digi | `[/path/to/pairs.slcio]` | Incoherent-pair overlay input file(s) (used with `--doOverlayIP`). |
| `--doFilterDL` | digi | `False` | Double-layer hit filtering in the vertex detector. |
| `--doTrackerConing` | digi + reco | `False` | Cone-filter the tracker hits around the signal MC particles (BIB cleaning). When enabled, the digi step writes the `…Coned` hit collections and the merger reads them before tracking. |
| `--RandSeed` | digi | `42` | Random seed for the digitisation smearing. |
| `--doTrackPerf` | reco | `False` | Run the tracking performance monitoring. |
| `--numThreads` | both | `1` | Number of threads. `1` runs serially; any value `> 1` enables the multi-threaded Gaudi Hive event loop with that many threads (scheduler + event slots) and sets the internal thread count of the CKF tracking and truth-matching algorithms; `0` auto-detects a sensible count from the CPU count. |

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
