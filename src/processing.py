import pandas as pd
import json
import os
import re
from datetime import timedelta

def aggregate_json_to_csv(json_dir, output_csv):
    all_data = []
    if not os.path.exists(json_dir): return None
    
    for fname in os.listdir(json_dir):
        if not fname.endswith('.json'): continue
        path = os.path.join(json_dir, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Flatten basics
            row = {
                "video_id": fname.replace(".json", ""),
                "url": data.get("metadata", {}).get("url", ""),
                "foco": data.get("foco", ""),
                "tom": data.get("tom", ""),
                "cenario": data.get("cenario", ""),
                "ocasiao_consumo": data.get("ocasiao_consumo", ""),
                "analise_visual": data.get("analise_visual", ""),
                "atencao": data.get("atencao", "")
            }
            # Flatten ABCD scores if they exist (added to config recently)
            scores = data.get("abcd_score", {})
            if scores:
                for k, v in scores.items():
                    row[f"score_{k}"] = v
            
            all_data.append(row)
        except Exception as e:
            print(f"Error reading {fname}: {e}")

    df = pd.DataFrame(all_data)
    if not df.empty:
        df.to_csv(output_csv, index=False)
    return df

def correlate_performance(performance_csv, schedule_csv, analysis_csv, output_csv):
    if not (os.path.exists(performance_csv) and os.path.exists(schedule_csv) and os.path.exists(analysis_csv)):
        print("Missing input files for correlation.")
        return None

    df_perf = pd.read_csv(performance_csv)
    df_sched = pd.read_csv(schedule_csv)
    df_analysis = pd.read_csv(analysis_csv)

    # 1. Parse Dates & Clean Data
    df_perf['day'] = pd.to_datetime(df_perf['day'])
    if 'PerformanceMetric' in df_perf.columns and df_perf['PerformanceMetric'].dtype == 'object':
        df_perf['PerformanceMetric'] = df_perf['PerformanceMetric'].str.rstrip('%').astype(float)

    # 2. Build Daily Creative Map
    daily_creatives = {}
    
    def get_vid(url):
        if not isinstance(url, str): return None
        m = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
        return m.group(1) if m else None

    # Lookup for analysis attributes
    creative_lookup = df_analysis.set_index('video_id').to_dict('index')

    link_cols = [c for c in df_sched.columns if 'Link' in c]
    for _, row in df_sched.iterrows():
        try:
            start = pd.to_datetime(row['Início'], format="%d/%m/%Y")
            end = pd.to_datetime(row['Fim'], format="%d/%m/%Y")
        except: continue
        
        ids = []
        for c in link_cols:
            vid = get_vid(row.get(c))
            if vid: ids.append(vid)
        
        curr = start
        while curr <= end:
            if curr not in daily_creatives: daily_creatives[curr] = set()
            daily_creatives[curr].update(ids)
            curr += timedelta(days=1)

    # 3. Calculate Mix Stats
    mix_rows = []
    for date, ids in daily_creatives.items():
        if not ids: continue
        
        stats = {'emotional': 0, 'rational': 0, 'product': 0, 'brand': 0, 'total': len(ids)}
        active_list = list(ids)
        
        for vid in ids:
            attrs = creative_lookup.get(vid, {})
            tone = str(attrs.get('tom', '')).lower()
            focus = str(attrs.get('foco', '')).lower()
            
            if 'emocional' in tone: stats['emotional'] += 1
            if 'racional' in tone: stats['rational'] += 1
            if 'produto' in focus: stats['product'] += 1
            if 'marca' in focus or 'brand' in focus: stats['brand'] += 1
            
        mix_rows.append({
            'day': date,
            'active_creatives_count': stats['total'],
            'mix_emotional_pct': (stats['emotional']/stats['total'])*100,
            'mix_rational_pct': (stats['rational']/stats['total'])*100,
            'mix_product_pct': (stats['product']/stats['total'])*100,
            'mix_brand_pct': (stats['brand']/stats['total'])*100,
            'active_video_ids': ",".join(active_list)
        })

    df_mix = pd.DataFrame(mix_rows)
    final_df = pd.merge(df_perf, df_mix, on='day', how='inner')
    final_df.to_csv(output_csv, index=False)
    return final_df

def get_portfolio_summary(analysis_csv):
    df = pd.read_csv(analysis_csv)
    return {
        "total_videos": len(df),
        "foco_distribution": df['foco'].value_counts(normalize=True).to_dict(),
        "tom_distribution": df['tom'].value_counts(normalize=True).to_dict(),
        "top_scenarios": df['cenario'].value_counts().head(5).to_dict(),
        "top_occasions": df['ocasiao_consumo'].value_counts().head(5).to_dict()
    }

def get_top_bottom_insights(performance_mix_csv, analysis_csv, n=20):
    df = pd.read_csv(performance_mix_csv)
    df_meta = pd.read_csv(analysis_csv)
    
    df = df.sort_values('PerformanceMetric', ascending=False)
    top = df.head(n)
    bot = df.tail(n)
    
    # Video Net Score
    def count_vids(dframe):
        c = {}
        for _, r in dframe.iterrows():
            if pd.isna(r['active_video_ids']): continue
            for v in r['active_video_ids'].split(','):
                c[v] = c.get(v, 0) + 1
        return c

    top_c = count_vids(top)
    bot_c = count_vids(bot)
    all_v = set(top_c.keys()) | set(bot_c.keys())
    
    scores = []
    for v in all_v:
        net = top_c.get(v,0) - bot_c.get(v,0)
        scores.append({'video_id': v, 'net_score': net})
    
    scores.sort(key=lambda x: x['net_score'], reverse=True)
    
    return {
        'top_performers': scores[:5],
        'bottom_performers': scores[-5:]
    }
