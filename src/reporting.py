import os
import json
import base64
import google.generativeai as genai
from .config import GEMINI_MODEL_NAME

def generate_html_report(insights_data, portfolio_summary, correlation_data, video_metrics, analysis_dir, viz_dir, output_file, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    # 1. Load Detailed Analysis
    top_ids = [x['video_id'] for x in insights_data.get('top_performers', [])]
    bot_ids = [x['video_id'] for x in insights_data.get('bottom_performers', [])]
    
    details = []
    for vid in set(top_ids + bot_ids):
        path = os.path.join(analysis_dir, f"{vid}.json")
        if os.path.exists(path):
            try:
                data = json.load(open(path, encoding='utf-8'))
                data['video_id'] = vid
                metrics = video_metrics.get(vid, {})
                data['secondary_metrics'] = {
                    'views': metrics.get('view_count', 'N/A'),
                    'likes': metrics.get('like_count', 'N/A'),
                    'title': metrics.get('title', 'Unknown')
                }
                details.append(data)
            except: continue

    # 2. Load Heatmap Image (Base64)
    img_path = os.path.join(viz_dir, "heatmap.png")
    img_b64 = ""
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode('utf-8')

    # 3. Construct Robust Prompt with Specific CSS
    prompt = f"""
Você é um Consultor Sênior de Estratégia de Marca (nível MBB/Big 4).
Seu objetivo é criar um RELATÓRIO ESTRATÉGICO PROFUNDO sobre a eficácia dos criativos.
O relatório deve ser analítico, detalhado e visualmente limpo.

--- DADOS DE ENTRADA ---
1. PANORAMA DO PORTFÓLIO: {json.dumps(portfolio_summary, ensure_ascii=False, indent=2)}
2. DRIVERS DE PERFORMANCE (Correlação com KPI): {json.dumps(correlation_data, ensure_ascii=False, indent=2)}
3. COMPARAÇÃO TOP vs BOTTOM: {json.dumps(insights_data, ensure_ascii=False, indent=2)}
4. DETALHAMENTO DOS VÍDEOS: {json.dumps(details, ensure_ascii=False, indent=2)}

--- REGRAS DE ANONIMIZAÇÃO ---
- NUNCA use nomes de marcas específicas ou nomes de métricas proprietárias. Use "A Marca" e "KPI de Negócio".

--- ESTRUTURA HTML E CSS (OBRIGATÓRIO) ---
Use este CSS no <head> para garantir a formatação Premium:
<style>
    :root {{ --brand-primary: #F40009; --dark-gray: #2b2b2b; --light-gray: #f4f4f4; --white: #ffffff; }}
    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: var(--dark-gray); line-height: 1.6; margin: 0; padding: 0; background-color: var(--light-gray); }}
    .container {{ max-width: 1000px; margin: 0 auto; background: var(--white); padding: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
    header {{ border-bottom: 3px solid var(--brand-primary); padding-bottom: 20px; margin-bottom: 40px; display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-weight: bold; font-size: 24px; color: var(--brand-primary); text-transform: uppercase; letter-spacing: 2px; }}
    .confidential {{ font-size: 12px; color: #999; text-transform: uppercase; }}
    h1 {{ font-size: 32px; margin-bottom: 10px; font-weight: 700; }}
    h2 {{ font-size: 22px; color: var(--brand-primary); margin-top: 30px; border-left: 4px solid var(--brand-primary); padding-left: 15px; text-transform: uppercase; }}
    h3 {{ font-size: 18px; color: var(--dark-gray); margin-top: 20px; }}
    .executive-summary {{ background-color: #fff8f8; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
    .stat-card {{ background: var(--light-gray); padding: 20px; border-radius: 8px; text-align: center; }}
    .stat-value {{ display: block; font-size: 28px; font-weight: bold; color: var(--brand-primary); }}
    .stat-label {{ font-size: 14px; text-transform: uppercase; color: #666; }}
    .insight-box {{ background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-top: 10px; }}
    .champion {{ border-top: 4px solid #28a745; }}
    .underperformer {{ border-top: 4px solid #dc3545; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }}
    .badge-brand {{ background: #fee2e2; color: #991b1b; }}
    .badge-product {{ background: #e0f2fe; color: #075985; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #fff; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
    th {{ background-color: var(--brand-primary); color: white; padding: 15px; text-align: left; }}
    td {{ padding: 15px; border-bottom: 1px solid #eee; font-size: 14px; }}
    .technical-appendix {{ margin-top: 50px; border-top: 1px solid #ddd; padding-top: 20px; }}
</style>

--- CONTEÚDO DO RELATÓRIO ---
1. **Header**: Logo "Strategic Insights" e texto "Strictly Confidential".
2. **Título**: "Relatório Final: Eficácia de Criativos".
3. **Executive Summary**: Resumo estratégico de alto impacto.
4. **Grid de Estatísticas**: 4 cartões com dados reais (Mix de Marca, Tom, etc).
5. **Diagnóstico da Estratégia de Marca**: Análise da distribuição e evolução.
6. **Champions (Por que funcionam?)**: Análise + Tabela detalhada.
7. **Underperformers (Onde falharam?)**: Análise + Tabela detalhada.
8. **Recomendações Estratégicas**: Próximos passos.
9. **Apêndices**:
   - Apêndice A: [IMAGEM_HEATMAP_PLACEHOLDER]
   - Apêndice B: [TECHNICAL_APPENDIX_PLACEHOLDER]

Gere APENAS o código HTML completo.
"""

    print("Gerando Relatório Premium com Gemini...")
    response = model.generate_content(prompt)
    html_content = response.text.strip()
    
    if html_content.startswith("```html"):
        html_content = html_content.replace("```html", "").replace("```", "")
    
    # 4. Inject Image
    if img_b64:
        image_tag = f'<div style="text-align:center; margin: 30px 0;"><img src="data:image/png;base64,{img_b64}" style="max-width:100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"><p style="font-size:12px; color:#666;">Figura 1: Matriz de Correlação - Drivers de KPI de Negócio</p></div>'
        
        if "[IMAGEM_HEATMAP_PLACEHOLDER]" in html_content:
            html_content = html_content.replace("[IMAGEM_HEATMAP_PLACEHOLDER]", image_tag)
        else:
            if "</body>" in html_content:
                html_content = html_content.replace("</body>", f"{image_tag}</body>")
            else:
                html_content += image_tag

    # 5. Inject Hardcoded Technical Appendix (Styled to match the report)
    technical_appendix = """
    <section class="technical-appendix">
        <h2>Apêndice B: Metodologia Técnica</h2>
        <p>Este relatório utiliza uma pipeline automatizada de IA para auditar, analisar e otimizar criativos de vídeo, conectando atributos qualitativos (Framework ABCD) com métricas de negócio.</p>
        
        <h3>1. Aquisição & Métricas</h3>
        <p>Os vídeos são processados e metadados públicos (visualizações, likes) são coletados para fornecer contexto de alcance ("Métricas de Vaidade"), embora o sucesso seja definido pelo impacto no KPI de negócio.</p>

        <h3>2. Análise Multimodal (Gemini AI)</h3>
        <p>Cada vídeo é processado frame-a-frame por IA para extrair dados estruturados:
           <ul>
             <li><strong>ABCD Framework:</strong> Atenção, Branding, Conexão, Direção.</li>
             <li><strong>Classificação:</strong> Tom (Racional/Emocional) e Foco (Produto/Marca).</li>
           </ul>
        </p>

        <h3>3. Cálculo do Mix Criativo (Creative Mix)</h3>
        <p>Para correlacionar criativos com a performance diária, calculamos o "Mix Diário". Não analisamos anúncios isolados, mas a média ponderada dos atributos ativos no dia.
           <br><em>Exemplo:</em> Se no Dia X, 80% dos anúncios ativos eram "Emocionais", o dia recebe esse score, que é então correlacionado estatisticamente com o KPI de Negócio para identificar drivers de sucesso.</p>

        <h3>4. Atribuição & Correlação</h3>
        <p>O sistema cruza a série temporal do Mix Criativo com o KPI para identificar correlações estatísticas e o <strong>Net Score</strong> de cada vídeo (frequência em dias de alta performance vs. baixa performance).</p>
    </section>
    """
    
    if "[TECHNICAL_APPENDIX_PLACEHOLDER]" in html_content:
        html_content = html_content.replace("[TECHNICAL_APPENDIX_PLACEHOLDER]", technical_appendix)
    else:
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{technical_appendix}</body>")
        else:
            html_content += technical_appendix
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Relatório Premium gerado em: {output_file}")
