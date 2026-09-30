# Hybrid Machine Learning Model for Phishing Detection

---
| | |
|---|---|
| **Programme** | MSc Cyber Security and Forensic Information Technology |
| **School** | University of Portsmouth, School of Computing, United Kingdom |
| **Project Title** | Hybrid Machine Learning Model for Phishing Detection |
| **Year** | 2023/24 |
| **Supervisor** | Dr Asim Ali, Assoc Prof Alexander Gegov |
| **Student** | Perceval Maturure |
| **IEEE Conference Paper** | **Maturure, P**., Ali, A., & Gegov, A. (2024). **Hybrid machine learning model for phishing detection**. IEEE. [https://ieeexplore.ieee.org/document/10705257](https://ieeexplore.ieee.org/document/10705257) |
| **Project URL** | [phishing.tp-stack.co.uk](https://phishing.tp-stack.co.uk) |

---

## Project Component 1 – Machine Learning Model

Developed a Hybrid machine learning model for phishing detection.

**Technology:** Python 3, Anaconda, Jupyter Notebook

**Dataset:** URL-Phish: A Feature-Engineered Dataset for Phishing Detection ([https://data.mendeley.com/datasets/65z9twcx3r/2](https://data.mendeley.com/datasets/65z9twcx3r/2))

---

## Project Component 2 – Phishing Detection System

A web application that allows users to submit a URL and receive a real-time prediction of whether it is legitimate or phishing.

**Technology:** Django 4, Python 3, Podman, Podman Compose, PostgreSQL Database, Caddy

> The Compose file is standard Compose format, so it still runs under Docker Compose too. Swap `podman compose` for `docker compose` in any command below.

### Prerequisites (AlmaLinux / RHEL 8–9)

```bash
sudo dnf install -y podman container-selinux netavark aardvark-dns

# Compose provider: `podman compose` uses the docker-compose binary
# (docker-compose-plugin) against the Podman socket. Keep this package
# installed even after Docker Engine is removed.
rpm -q docker-compose-plugin
# Alternative provider: sudo dnf install -y epel-release podman-compose  (1.1+ required)

# Docker-compatible API socket and restart of containers at boot
sudo systemctl enable --now podman.socket
sudo systemctl enable podman-restart.service

# Optional: the docker command runs podman instead
sudo dnf install -y podman-docker && sudo touch /etc/containers/nodocker
```

### How to Run Locally

1. Clone the repository: `git clone <GitHub URL>`
2. cd into `msc_project/`
3. Build the images: `podman compose -f Docker-compose.yml build`
4. Start the application: `podman compose -f Docker-compose.yml up -d`
5. Check all three services are up: `podman compose -f Docker-compose.yml ps` (`db`, `web`, `caddy`)
6. Visit the site through Caddy on ports 80/443, at the domain set in `Caddyfile` ([phishing.tp-stack.co.uk](https://phishing.tp-stack.co.uk) in production). The `web` container only exposes port 8000 to the internal network, so `http://127.0.0.1:8000` isn't reachable from the host.

## Useful Podman Commands

- View running containers: `podman compose -f Docker-compose.yml ps` (or `podman ps`)
- View logs: `podman compose -f Docker-compose.yml logs -f`
- Stop the application: `podman compose -f Docker-compose.yml down`
- Rebuild and restart: `podman compose -f Docker-compose.yml up -d --build`
- Remove all containers and volumes: `podman compose -f Docker-compose.yml down -v`
- Restart a specific service: `podman compose -f Docker-compose.yml restart <service_name>`
- Access a container shell: `podman compose -f Docker-compose.yml exec <service_name> bash`
- List images / volumes: `podman images` / `podman volume ls`
- Clean up unused images and containers: `podman system prune`

## Podman Notes

- **SELinux:** the only bind mount, `./Caddyfile:/etc/caddy/Caddyfile:ro,Z`, carries the `Z` flag so Caddy can read the file under SELinux enforcing mode. All other mounts are named volumes, which Podman labels automatically. Any new bind mount needs `:Z` as well.
- **Restart on boot:** Podman has no daemon. All services use `restart: always` and are started at boot by `podman-restart.service`.
- **Healthcheck ordering:** `web` waits for `db` to be healthy (`depends_on: condition: service_healthy`). Use the docker-compose provider or podman-compose 1.1+, because older podman-compose versions don't honour this.
- **Slow first build:** when Compose builds through the Podman socket it may show only `Sending build context...` until the build finishes. It hasn't hung. Use `journalctl -u podman -f` to watch progress.
- **Compose provider message:** `>>>> Executing external compose provider ... <<<<` is informational. Hide it with:
  ```bash
  sudo mkdir -p /etc/containers/containers.conf.d
  printf '[engine]\ncompose_warning_logs = false\n' | sudo tee /etc/containers/containers.conf.d/compose.conf
  ```
- **Image names:** images are fully qualified (`docker.io/library/postgres:16`), so pulls work without relying on Podman's short-name resolution.

---

## Changelog

### Version 3.1 (09-2026) – Migration from Docker to Podman

#### 1. Container Runtime
- Migrated the production deployment on AlmaLinux from **Docker Engine** to **rootful Podman** (daemonless, SELinux-integrated, Red Hat-supported runtime).
- Enabled `podman.socket` for the Docker-compatible API and `podman-restart.service` so containers start automatically at boot.
- Networking now uses Podman's **netavark** and **aardvark-dns** for container-to-container name resolution between Django, PostgreSQL and Caddy.

#### 2. Compose Tooling
- Replaced `docker compose` with `podman compose`, keeping the project compatible with Docker for local development.
- `Docker-compose.yml` changes: removed the obsolete `version:` key, added the SELinux `Z` label to the Caddyfile bind mount, and fully qualified the image names (`docker.io/library/...`).
- Images are rebuilt from the Dockerfiles in the repository. No data needed migrating from Docker volumes.

#### 3. Documentation
- Updated the setup, run and command reference sections for Podman, and added AlmaLinux prerequisites and Podman-specific notes (SELinux, restart policy, healthcheck ordering, build output).
- Corrected the access instructions: the app is served through Caddy on ports 80/443, not directly on port 8000.

#### 4. Docker Engine Removal
- Disabled and removed `docker-ce`, `docker-ce-cli`, `containerd.io` and `docker-buildx-plugin`, keeping `docker-compose-plugin` as the Compose provider for `podman compose`.
- Optionally installed `podman-docker` so the `docker` command runs Podman.

---

### Version 3.0 (06-2026) – New Dataset & Enhanced Deployment

#### 1. New Dataset: URL-Phish (2026)
- Migrated from the 2023 Mendeley dataset to the **URL-Phish** dataset published in March 2026.
- The new dataset contains **116,600 unique URLs** (100,000 benign, 16,600 phishing samples) collected between November 2024 and September 2025.
- Features were re-engineered to match the new dataset's **25 features** (22 numerical + 3 reference columns), replacing the previous 41-feature set.
- Retrained the Hybrid Voting Classifier (both Hard and Soft Voting) on the new dataset, achieving improved detection accuracy.
- Updated `feature_names.pkl` to reflect the new feature order: `url_len`, `dom`, `dom_len`, `is_ip`, `tld`, `tld_len`, `subdom_cnt`, `letter_cnt`, `digit_cnt`, `special_cnt`, `eq_cnt`, `qm_cnt`, `amp_cnt`, `dot_cnt`, `dash_cnt`, `under_cnt`, `letter_ratio`, `digit_ratio`, `spec_ratio`, `is_https`, `slash_cnt`, `entropy`, `path_len`, `query_len`.

#### 2. Feature Extraction Update (`feature_extraction.py`)
- Completely rewrote the feature extraction module to compute all 25 features required by the new model.
- Added helper functions: `_is_ip_address()`, `_get_tld()`, `_get_domain()`, `_get_subdomains()` for accurate URL parsing.
- Ensured all features are extracted in the exact order expected by `feature_names.pkl`.

#### 3. Django Application Restructuring (`views.py`, `models.py`)
- Fixed import conflict by renaming the pickle files directory from `models/` to `trained_models/`, resolving the `ImportError` with Django's `models.py`.
- Updated `views.py` to load models from `trained_models/` with proper error handling and debugging output.
- Added probability scores to the database model (`probability_legitimate`, `probability_phishing`) for better result transparency.
- Integrated the new Hybrid Voting Classifier (Soft Voting) as the production model.

#### 4. Deployment Enhancements
- Switched from SQLite to **PostgreSQL** in production for better scalability and reliability.
- Added **Caddy** as the reverse proxy with automatic HTTPS termination.
- Added health checks and proper container orchestration with Docker Compose.
- Migrated database schema to include new fields and applied migrations automatically on container startup.

#### 5. Directory Structure
- Restructured the Django app to separate concerns:
  - `trained_models/` – Contains all `.pkl` files (models, scaler, feature names)
  - `models.py` – Django ORM models (URLCheck)
  - `feature_extraction.py` – URL feature extraction logic
  - `views.py` – Prediction logic and routing

---

### Version 2.0 (04-2026) – Hybrid Voting Classifier (All 41 Features)

#### 1. New Hybrid Voting Model (`Phishing_Hybrid_Voting.ipynb`)
- Combined Decision Tree and Random Forest classifiers into a single **Hybrid Voting Classifier** using scikit-learn's `VotingClassifier`.
- Implemented both **Hard Voting** (majority vote) and **Soft Voting** (averaged probabilities) strategies.
- Trained the hybrid model using **all 41 features** from the original dataset to maximise detection accuracy and reduce false positives.
- Added comprehensive comparative analysis across all metrics: Accuracy, Precision, Recall, F1-Score, ROC AUC, and MCC.
- Added visualisations: per-metric bar charts, side-by-side confusion matrices, ROC curves, and grouped bar charts.
- Exported trained model artifacts: `phishing_hybrid_voting_hard.pkl`, `phishing_hybrid_voting_soft.pkl`, `standard_scaler.pkl`, and `feature_names.pkl`.

#### 2. Updated Django Application (`views.py`)
- Integrated the Hybrid Voting Classifier (Hard Voting) as the prediction model, replacing the standalone Random Forest model.
- Added **StandardScaler** integration — the scaler fitted during training is now applied to user-submitted URLs before prediction.
- Added feature ordering using `feature_names.pkl` to guarantee features are passed to the model in the exact same column order as during training.
- Added missing feature validation with clear error messages to help debug any mismatches.

#### 3. New Feature Extraction Module (`feature_extraction.py`)
- Created a new module that automatically extracts all 41 URL features from any user-submitted URL.
- Features are extracted by parsing the URL and computing character counts, domain analysis, path/query detection, and Shannon entropy.
- Returns a dictionary of features which is then ordered by `feature_names.pkl`.

#### 4. Why All 41 Features Instead of 13
The initial version used only 13 features selected from feature importance analysis. This caused **false positives** where legitimate URLs (e.g., `amazon.co.uk`) were incorrectly flagged as phishing. Switching to all 41 features provided the model with richer contextual information, reducing misclassifications and improving overall prediction reliability.

---
## Resources

### Dataset
- **URL-Phish Dataset**: [https://data.mendeley.com/datasets/65z9twcx3r/2](https://data.mendeley.com/datasets/65z9twcx3r/2)
- **Original Dataset (2023)**: [https://data.mendeley.com/datasets/6tm2d6sz7p/1](https://data.mendeley.com/datasets/6tm2d6sz7p/1)

### Container Tooling
- [Podman Documentation](https://docs.podman.io)
- [podman-compose](https://github.com/containers/podman-compose)

### Tutorials
- [Django Tutorial – Tech with Tim](https://www.youtube.com/watch?v=uu98pqiUJU8&list=PLEsfXFp6DpzTD1BD1aWNxS2Ep06vIkaeW)
- [Django Tutorial – Corey Schafer](https://www.youtube.com/watch?v=UmljXZIypDc&list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p)

### Research References
- Maturure, P., Ali, A., & Gegov, A. (2024). **Hybrid machine learning model for phishing detection**. IEEE. [https://ieeexplore.ieee.org/document/10705257](https://ieeexplore.ieee.org/document/10705257)
- PhishTank: [https://phishtank.org](https://phishtank.org)
- Research Organization Registry (ROR): [https://ror.org](https://ror.org)