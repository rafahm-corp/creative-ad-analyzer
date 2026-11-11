import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.acquisition import fetch_metrics, get_video_id
from src.analysis import analyze_video_by_url
from src.processing import aggregate_json_to_csv, correlate_performance, get_portfolio_summary, get_top_bottom_insights
from src.reporting import generate_html_report
from src.visualization import generate_visualizations
from src.config import OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(description="Creative Ad Analyzer Orchestrator")
    parser.add_argument("--brand", required=True, help="Brand name (e.g., Coca-Cola)")
    parser.add_argument("--urls", required=True, help="Path to text file with YouTube URLs")
    parser.add_argument("--perf", help="Path to daily performance CSV")
    parser.add_argument("--sched", help="Path to schedule CSV")
    
    args = parser.parse_args()
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.")
        return

    # Setup directories
    brand_dir = OUTPUT_DIR / args.brand
    videos_dir = brand_dir / "videos"
    analysis_dir = brand_dir / "analysis"
    viz_dir = brand_dir / "visualizations"
    
    for d in [videos_dir, analysis_dir, viz_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Load URLs
    with open(args.urls, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"--- Starting Pipeline for {args.brand} ({len(urls)} videos) ---")

    # 2. Acquisition & Metrics
    print("\n[1/5] Fetching video metrics...")
    metrics = fetch_metrics(urls, output_file=brand_dir / "metrics.json")

    # 3. Multimodal Analysis
    print("\n[2/5] Running Gemini Multimodal Analysis (Direct URL prompt)...")
    for url in urls:
        video_id = get_video_id(url)
        if not video_id:
            print(f"  - Skipping invalid URL: {url}")
            continue
        output_json = analysis_dir / f"{video_id}.json"
        analyze_video_by_url(url, api_key, output_json)

    # 4. Data Processing
    print("\n[3/5] Aggregating results and calculating correlations...")
    master_csv = brand_dir / "master_analysis.csv"
    aggregate_json_to_csv(analysis_dir, master_csv)
    
    correlation_data = None
    if args.perf and args.sched:
        mix_perf_csv = brand_dir / "creative_mix_performance.csv"
        correlation_data = correlate_performance(args.perf, args.sched, master_csv, mix_perf_csv)

    # 5. Visualization
    print("\n[4/5] Generating visualizations...")
    if correlation_data is not None:
        generate_visualizations(brand_dir / "creative_mix_performance.csv", viz_dir)

    # 6. Reporting
    print("\n[5/5] Synthesizing final report...")
    portfolio_summary = get_portfolio_summary(master_csv)
    insights = get_top_bottom_insights(brand_dir / "creative_mix_performance.csv", master_csv) if correlation_data is not None else {}
    
    generate_html_report(
        insights_data=insights,
        portfolio_summary=portfolio_summary,
        correlation_data=correlation_data.to_dict() if correlation_data is not None else {},
        video_metrics=metrics,
        analysis_dir=analysis_dir,
        viz_dir=viz_dir,
        output_file=brand_dir / "final_report.html",
        api_key=api_key
    )

    print(f"\n--- Pipeline Complete! ---")
    print(f"Final Report: {brand_dir / 'final_report.html'}")

if __name__ == "__main__":
    main()
