# Creative Ad Analyzer

**An AI-Powered Video Strategy Platform**

(THIS IS NOT AN OFFICIAL GOOGLE TOOL)

This project is an automated pipeline designed to audit, analyze, and optimize video advertising creatives using Google's **Gemini Multimodal AI** (`gemini-3.6-flash`). It moves beyond manual review to provide data-driven insights connecting Creative Attributes (ABCD Framework, Tone, Focus) with Business Performance (Sales, Conversion, etc.).

## Key Features

*   **Native Multimodal Analysis:** Processes public YouTube URLs directly using **Gemini 3.6 Flash** to analyze video creatives without requiring third-party video downloaders.
*   **Google ABCD Framework:** Automatically scores videos against the **Google ABCD Framework** (Attention, Branding, Connection, Direction).
*   **Engagement Metrics:** Fetches engagement metrics using the official **YouTube Data API v3**.
*   **Performance Correlation:** Merges creative data with daily performance logs to identify "Winning Mixes" (e.g., "Emotional Brand ads drive +20% lift").
*   **Strategic Reporting:** Generates a premium HTML Executive Deck with visualizations, deep dives into "Champion" vs. "Underperformer" creatives, and actionable hypotheses.
*   **Interactive Web UI & CLI:** Run via Streamlit Web App (`app.py`) or command-line orchestrator (`orchestrator.py`).

## Project Structure

```text
creative-ad-analyzer/
├── inputs/                 # Input data (performance CSVs, schedules)
├── outputs/                # Generated artifacts
│   └── BrandName/          # Brand-specific outputs
│       ├── analysis/       # Individual JSON analysis per video
│       ├── visualizations/ # Correlation heatmaps & charts
│       ├── master_analysis.csv
│       └── final_report.html
├── src/                    # Core modules
│   ├── acquisition.py      # YouTube Data API Metrics
│   ├── analysis.py         # Gemini API Wrapper (Direct URL / Multimodal)
│   ├── config.py           # Settings & Prompts
│   ├── processing.py       # Data Aggregation & Logic
│   ├── reporting.py        # HTML Generation
│   └── visualization.py    # Plotting
├── orchestrator.py         # Main CLI entry point
├── app.py                  # Streamlit Web UI
└── requirements.txt        # Python dependencies
```

## Installation

1.  **Prerequisites:**
    *   Python 3.10+
    *   Google Gemini API Key / YouTube Data API Key

2.  **Setup:**
    ```bash
    # Clone the repository
    git clone https://github.com/rafahm-google/creative-ad-analyzer.git
    cd creative-ad-analyzer

    # Create Virtual Environment
    python3 -m venv venv
    source venv/bin/activate

    # Install Dependencies
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    *   Create a `.env` file in the root directory:
        ```env
        GEMINI_API_KEY="your_api_key_here"
        YOUTUBE_API_KEY="your_api_key_here"
        ```

## Usage

### Streamlit Web Interface:
```bash
streamlit run app.py
```

### Command-Line Orchestrator:
```bash
python3 orchestrator.py --brand "BrandName" --urls "path/to/urls.txt" --perf "path/to/performance.csv" --sched "path/to/schedule.csv"
```

### Input Data Formats
To help you get started, we have provided templates for performance correlation:
- **`performance_template.csv`**: Contains daily metrics. Requires `day` (YYYY-MM-DD) and `PerformanceMetric` (percentage or float) columns.
- **`schedule_template.csv`**: Maps videos to date ranges. Requires `Início` (DD/MM/YYYY), `Fim` (DD/MM/YYYY), and columns containing `Link` in their name for the YouTube URLs.

**Parameters:**
*   `--brand`: Name of the brand (creates a subfolder in `outputs/`).
*   `--urls`: Text file with one YouTube URL per line.
*   `--perf`: (Optional) Daily performance CSV (Columns: `day`, `MetricName`).
*   `--sched`: (Optional) Schedule CSV mapping dates to video links.

**Example:**
```bash
python3 orchestrator.py \
  --brand "Coca-Cola" \
  --urls "schedule_urls.txt" \
  --perf "performance_template.csv" \
  --sched "schedule_template.csv"
```

## Outputs

After a successful run, check `outputs/{BrandName}/`:

1.  **`final_report.html`**: A standalone, interactive Executive Report containing:
    *   **Executive Summary:** The "verdict" on creative strategy.
    *   **Champion Analysis:** Why top ads worked (ABCD breakdown).
    *   **Underperformer Autopsy:** Why bottom ads failed.
    *   **Visual Appendix:** Correlation heatmaps embedded directly in the file.
2.  **`master_analysis.csv`**: A granular dataset of every video's attributes (Tone, Focus, Visual Description, Transcription).
3.  **`creative_mix_performance.csv`**: Daily time-series showing the "Creative Recipe" vs. Business Results.

## Methodology

1.  **Ingest:** Video engagement metrics are fetched via the official YouTube Data API v3.
2.  **Analyze:** `gemini-3.6-flash` analyzes video content directly from public YouTube URLs to extract qualitative data (Scene description, Sentiment, Brand cues, ABCD Scores).
3.  **Correlate:** The system maps the active creative mix (e.g., "Today was 80% Emotional") to the daily performance metric.
4.  **Synthesize:** A final LLM pass acts as a "Senior Consultant," reviewing the statistical and qualitative data to write the final strategy document.
