# MAIAConfig

Package for key4hep configuration files related to the MAIA detector concept.

The configuration scripts are imported from
[mucoll-benchmarks](https://github.com/MuonColliderSoft/mucoll-benchmarks) and
organised, as closely as possible, to mirror the layout of
[CLDConfig](https://github.com/key4hep/CLDConfig/tree/main/CLDConfig).

## Layout

All steering files and components live under [MAIAConfig/](MAIAConfig), grouped by
domain (following the CLDConfig convention):

- `digi_steer.py` / `reco_steer.py` — the digitisation and reconstruction entry
  points (run with `k4run`).
- `digiAlgList.py` / `recoAlgList.py` — assemble the per-step algorithm lists.
- `digi_args.py` / `reco_args.py` — command-line argument parsers.
- `muc_mt.py`, `muc_services.py`, `event_counter.py` — shared services and
  multi-threading helpers.
- `CaloDigi/` — ECal, HCal and Muon calorimeter digitisation/reconstruction.
- `Tracking/` — tracker digitisation, hit merging, CKF tracking and filtering.
- `Overlay/` — beam-induced-background (BIB) overlay.
- `ParticleFlow/` — Pandora PFA and jet clustering.
- `Diagnostics/` — tracking performance monitoring.
- `PandoraSettingsMAIA/` — Pandora steering and likelihood data XMLs (must be
  present in the directory where reconstruction is run).

## Usage

The geometry and tracking inputs are taken from environment variables (with
command-line overrides available). Typically these are set from the installed
`k4geo` / `k4ActsTracking` data:

| Variable            | Meaning                                   |
| ------------------- | ----------------------------------------- |
| `MUCOLL_GEO`        | Compact detector description (XML)        |
| `MUCOLL_GEOM_NAME`  | Detector schema name (e.g. `MAIA_v0`)     |
| `MUCOLL_MATMAP`     | Material maps file for tracking           |
| `MUCOLL_TGEO`       | TGeometry file for tracking               |
| `MUCOLL_TGEO_DESC`  | TGeometry subdetector JSON for tracking   |

Run the chain from inside the `MAIAConfig/` directory:

```bash
# 1. Simulation (DD4hep) -> sim_output.edm4hep.root
ddsim --compactFile $MUCOLL_GEO -G -N 10 \
      --gun.particle mu- --gun.distribution uniform \
      --outputFile sim_output.edm4hep.root

# 2. Digitisation -> digi_output.edm4hep.root
k4run digi_steer.py --DD4hepXMLFile $MUCOLL_GEO

# 3. Reconstruction -> reco_output.edm4hep.root
k4run reco_steer.py --DD4hepXMLFile $MUCOLL_GEO --DetectorSchema MAIA_v0
```

Use `k4run --help digi_steer.py` (or `reco_steer.py`) to list all available
options, e.g. `--doOverlayFull`, `--doFilterDL`, `--doTrackPerf`, `--useMT`.
