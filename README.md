# 🃏 Euchre Stats

A Python-based web app to track, visualize, and analyze Euchre games played with custom house rules.

## Quick Start 🚀

If you already have the repo cloned and dependencies installed:

```bash
cd Euchre_Stats
source venv/bin/activate  # Activate virtual environment
streamlit run app.py --server.port 8504  # Use port 8504 if 8501 is busy
```

Open your browser to `http://localhost:8504`

## Features

- **Live Scorekeeping**: Log each hand with flexible, explicit scoring inputs
- **Historical Game Storage**: View all past games with complete hand logs
- **Per-Game Analytics**: Score progression charts, call breakdowns, euchre rates
- **Cross-Game Statistics**: Player stats, team stats, most common calls

## House Rules Supported

- Games with any number of players per team (typically 3v3)
- Configurable target score (default: 32 points)
- Any call value (3, 4, 5, 6, Partner Best, Alone, custom)
- Manual point entry (not auto-calculated from call value)
- Euchre tracking with customizable penalty points
- Negative scores allowed

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/KingAragon93/Euchre_Stats.git
cd Euchre_Stats
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## Troubleshooting 🔧

### Port Already in Use
If you see "Port 8501 is already in use":
```bash
# Try a different port
streamlit run app.py --server.port 8502
# Or kill existing processes
pkill -f streamlit
```

### Virtual Environment Issues
```bash
# If venv activation fails
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Streamlit Command Not Found
```bash
# Make sure venv is activated
source venv/bin/activate
# Or install streamlit globally
pip install streamlit
```

### Database Connection Issues
- The app uses Google Cloud Firestore for data storage
- For local development, ensure you have GCS credentials set up (see Data Storage section)
- If GCS fails, the app will work locally with SQLite fallback

## Usage

### Starting a New Game

1. Go to **➕ New Game**
2. Enter team names and player names (one per line)
3. Set the target score (default: 32)
4. Click **Start Game**

### Logging Hands

1. Go to **🎮 Active Games**
2. Select the caller from the dropdown
3. Select what was called (3, 4, 5, 6, Partner Best, etc.)
4. Enter points scored by the caller
5. Check "Was it a Euchre?" if applicable
   - If euchred, enter points for the other team
6. Add optional notes
7. Click **Log Hand**

### Scoring Logic

- **Normal hand**: Caller's team gains the points scored
- **Euchre**: Caller's team loses points scored, other team gains euchre points

### Viewing Statistics

- **Per-game**: Score chart, hand log, call breakdown
- **Overall**: Player stats, team stats, call value analysis

## Project Structure

```
Euchre_Stats/
├── app.py           # Streamlit UI
├── database.py      # SQLite persistence layer
├── models.py        # Data classes and types
├── analytics.py     # Pandas-based analysis
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

### Render

1. Create a new Web Service
2. Connect your repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

## Data Storage

The app uses SQLite for local data management, synced to **Google Cloud Storage** (bucket: `euchrestats`) for persistence across deployments.

### Google Cloud Storage Setup

The app requires GCS authentication. Choose one of these methods:

#### For Local Development

**Option A: Google Cloud CLI (Recommended)**
```bash
# Install gcloud CLI, then:
gcloud auth application-default login
```

**Option B: Service Account File**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

**Option C: JSON in Environment Variable**
```bash
export GCS_CREDENTIALS_JSON='{"type":"service_account",...}'
```

#### For Streamlit Cloud Deployment

1. Create a service account in Google Cloud Console with **Storage Object Admin** role on the `euchrestats` bucket
2. Download the service account JSON key
3. In Streamlit Cloud, go to your app's settings → **Secrets**
4. Add the service account JSON under `gcp_service_account`:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

### Database Sync Behavior

- **On startup**: Downloads `euchre_stats.db` from GCS (if exists)
- **After writes**: Automatically uploads changes to GCS
- **Local fallback**: Works locally without GCS if authentication fails

### Tables

- **games**: Team info, scores, status, target score
- **hands**: Hand-by-hand data with cumulative scores

## Future Enhancements

- [ ] Authentication/user accounts
- [ ] Export data to CSV
- [ ] Advanced visualizations
- [ ] Tournament mode
- [ ] Mobile app (React Native)

## License

MIT License
