import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_visualizations(csv_path, output_dir):
    if not os.path.exists(csv_path): return
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(csv_path)
    cols = ['PerformanceMetric', 'mix_emotional_pct', 'mix_rational_pct' 'mix_product_pct', 'mix_brand_pct']
    cols = [c for c in cols if c in df.columns]
    
    if len(cols) < 2: return

    # Heatmap
    plt.figure(figsize=(8,6))
    sns.heatmap(df[cols].corr(), annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap.png'))
    plt.close()
