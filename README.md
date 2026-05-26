# Attendance Tracker API

A lightweight, data-driven Flask web application developed to track academic attendance metrics against an 85% compliance threshold. The system computes real-time predictive buffers, consecutive attendance targets, and structural risk tiers to help students manage eligibility requirements.

---

## Installation and Setup

| Step | Process | Action / Command |
| :--- | :--- | :--- |
| 1 | Clone Project | Navigate into the repository root directory |
| 2 | Virtual Environment | Initialize environment with `python3 -m venv venv` |
| 3 | Activate Environment (Unix) | Execute `source venv/bin/activate` |
| 4 | Activate Environment (Windows)| Execute `venv\Scripts\activate` |
| 5 | Install Dependencies | Execute `pip install Flask` |
| 6 | Execution | Run the local server via `python app.py` |

---

## API Reference Endpoints

| Endpoint | HTTP Method | Payload Requirements | Functional Description |
| :--- | :--- | :--- | :--- |
| `/` | GET | None | Serves the primary user interface template. |
| `/api/data` | GET | None | Retrieves all subjects with calculated stats and runtime analytics. |
| `/api/mark` | POST | `{"subject_id": "string", "status": "present"}` | Records attendance. Valid status strings are `present` or `absent`. |
| `/api/rename` | POST | `{"subject_id": "string", "name": "string"}` | Modifies a course label. Rejects empty string arguments with a 400 error. |
| `/api/reset` | POST | `{"subject_id": "string"}` | Resets session records for the designated course identifier back to 0. |

---

## Business Logic and Rule Engine Calculations

Backend computations are determined automatically using an 85% operational performance threshold:

| Computed Metric | Internal Algorithmic Rule | Risk Evaluation Category |
| :--- | :--- | :--- |
| Attendance Percentage | `(attended / total) * 100` | Dynamic based on total values |
| Skippable Classes Buffer | `int((attended - 0.85 * total) / 0.85)` | Active when ratio is >= 85% (Safe Status) |
| Consecutive Attendance Required | `math.ceil((0.85 * total - attended) / 0.15)` | Active when ratio is < 85% (Warning/Critical Status) |
| Warning Threshold Tier | Condition met if `75% <= percentage < 85%` | Represents moderate risk of non-compliance |
| Critical Threshold Tier | Condition met if `percentage < 75%` | Represents acute risk of eligibility forfeiture |

---

## Data Storage and File Lifecycle

| Component Architecture | Engineering System Specification |
| :--- | :--- |
| Persistence Engine | Structured local file-system serialization utilizing Python native JSON parsing. |
| Storage Target Location | Persisted within the local core execution directory as a `data.json` file asset. |
| Bootstrap Routine | Automatically provisions 6 standard academic courses if no persistence file is found. |
| Lifecycle Control | Independent file streams open, decode, mutate, serialize, and terminate per transaction block. |
