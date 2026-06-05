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
- `digi_reco_steer.py` — combined entry point that runs digitisation and
  reconstruction in a single `k4run` job (no intermediate digi file).
- `digiAlgList.py` / `recoAlgList.py` — assemble the per-step algorithm lists.
- `digi_args.py` / `reco_args.py` — command-line argument parsers.
- `Common/` — shared helpers used by every steering macro: `steering.py`
  (service + ApplicationMgr wiring), `muc_mt.py` (multi-threading),
  `muc_services.py` (services), `event_counter.py`.
- `CaloDigi/` — ECal, HCal and Muon calorimeter digitisation/reconstruction.
- `TrackerDigi/` — tracker digitisation (vertex/inner/outer) and double-layer filtering.
- `Tracking/` — hit merging and CKF track reconstruction.
- `Overlay/` — beam-induced-background (BIB) overlay.
- `ParticleFlow/` — Pandora PFA and jet clustering.
- `Diagnostics/` — tracking performance monitoring.
- `PandoraSettings/` — Pandora steering and likelihood data XMLs (must be
  present in the directory where reconstruction is run).

## Usage

The detector geometry is taken from an environment variable (with a
command-line override available). It is typically set from the installed
`k4geo` data:

| Variable            | Meaning                                   |
| ------------------- | ----------------------------------------- |
| `MUCOLL_GEO`        | Compact detector description (XML)        |

Run the chain from inside the `MAIAConfig/` directory:

```bash
# 1. Simulation (DD4hep) -> sim_output.edm4hep.root
ddsim --compactFile $MUCOLL_GEO -G -N 10 \
      --gun.particle mu- --gun.distribution uniform \
      --outputFile sim_output.edm4hep.root

# 2. Digitisation -> digi_output.edm4hep.root
k4run digi_steer.py --DD4hepXMLFile $MUCOLL_GEO

# 3. Reconstruction -> reco_output.edm4hep.root
k4run reco_steer.py --DD4hepXMLFile $MUCOLL_GEO
```

Alternatively, run digitisation and reconstruction together in one job
(reads `sim_output.edm4hep.root`, writes `digireco_output.edm4hep.root`):

```bash
k4run digi_reco_steer.py --DD4hepXMLFile $MUCOLL_GEO
```

Use `k4run --help digi_steer.py` (or `reco_steer.py`) to list all available
options, e.g. `--doOverlayFull`, `--doFilterDL`, `--doTrackPerf`, `--useMT`.
