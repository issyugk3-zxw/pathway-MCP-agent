import matplotlib.pyplot as plt
import matplotlib
import math
from pathlib import Path

matplotlib.use("Agg") 


def create_enrichment_barplot(
    terms: list,
    title: str = "Enrichment Analysis",
    output_path: str = None
) -> str:
    """
    Create a bar plot of the enrichment results.
    
    Args:
        terms:  Enrichr returned list of terms
        title: Title of the plot
        output_path: Path to save the plot
    
    Returns:
        Absolute path to the saved plot
    """
    if not terms:
        return "No terms to plot"
    
    # Extract data (Enrichr format: [rank, name, p-value, z-score, combined_score, genes, ...])
    names = []
    p_values = []
    gene_counts = []
    
    for term in terms:
        name = term[1]
        if len(name) > 45:
            name = name[:42] + "..."
        names.append(name)
        p_values.append(term[2])
        gene_counts.append(len(term[5]))
    
    # Calculate -log10(p-value)
    neg_log_p = [-math.log10(p) if p > 0 else 0 for p in p_values]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, max(6, len(terms) * 0.5)))
    
    # Color mapping
    max_val = max(neg_log_p) if neg_log_p else 1
    colors = plt.cm.RdYlBu_r([p / max_val for p in neg_log_p])
    
    # Horizontal bar plot
    bars = ax.barh(range(len(names)), neg_log_p, color=colors, edgecolor='darkgray')
    
    # Set labels
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel('-log10(P-value)', fontsize=11)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.invert_yaxis()  # Most significant on top
    
    # Add gene count labels
    for i, (bar, count) in enumerate(zip(bars, gene_counts)):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f'{count} genes', va='center', fontsize=8, color='gray')
    
    plt.tight_layout()
    
    if output_path is None:
        output_path = Path.cwd() / "enrichment_plot.png"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return str(Path(output_path).absolute())