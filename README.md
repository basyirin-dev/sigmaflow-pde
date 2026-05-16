# σFlow-PDE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

A drop-in **H-Bar training engine** that escapes the σ-trap in neural PDE solvers via live σ/δ/α ODE integration, autonomous phase curriculum, and auto-falsification.

---

## Overview

Neural PDE solvers (FNO, DeepONet, PINNs) are notorious for getting stuck in low-frequency, mean-predicting solutions — the **σ-trap**. σFlow-PDE introduces a training-time framework that:

- **Live σ/δ/α ODE integration** – Continuously evolves spectral coefficients during training to escape local spectral minima.
- **Autonomous phase curriculum** – Adaptively schedules training phases based on spectral convergence diagnostics.
- **Auto-falsification** – Automatically detects and rejects models that fail spectral consistency checks, ensuring robust generalization.

## Topics

`physics-ml` · `neural-operators` · `compositional-generalization` · `training-dynamics` · `pde-solver` · `h-bar-framework` · `ood-generalization` · `fno` · `deeponet` · `reproducible-ml`

## License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
