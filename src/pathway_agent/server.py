from mcp.server.fastmcp import FastMCP
from .enrichr import submit_gene_list, get_enrichment
from .file_reader import read_gene_list
from .visualization import create_enrichment_barplot
from .stringdb import get_interaction, get_interaction_partners, format_score

mcp = FastMCP("pathway-agent")

# Support databases
DATABASES = {
    "KEGG_2021_Human": "KEGG_2021_Human",
    "GO_Biological_Process_2021": "GO_Biological_Process_2021",
    "GO_Cellular_Component_2021": "GO_Cellular_Component_2021",
    "GO_Molecular_Function_2021": "GO_Molecular_Function_2021",
    "MSigDB_Hallmark_2020": "MSigDB Hallmark",
}



@mcp.tool()
async def hello_pathway(gene_name: str) -> str:
    """Return a greeting message for the given gene name."""
    return f"Hello! You asked about gene: {gene_name}"

@mcp.tool()
async def  perform_enrichment(gene_list: list[str], database: str = "KEGG_2021_Human", top_n: int = 10) -> dict:
    """
    Perform pathway enrichment analysis on a list of genes.
    
    Args:
        gene_list: List of gene symbols.
        database: Database to use for enrichment.
        top_n: Number of top results to return.
    
    Returns:
        Dictionary containing the enrichment results if successful, None otherwise.
    """
    submit_result = await submit_gene_list(gene_list)
    if not submit_result:
        return "Error: Failed to submit the gene list to Enrichr"
    
    
    user_list_id = submit_result["userListId"]
    enrichment_result = await get_enrichment(user_list_id, database)
    if not enrichment_result or database not in enrichment_result:
        return "Error: Failed to get the enrichment results from Enrichr"
    
    terms = enrichment_result[database][:top_n]
    result_lines = [
        f"Enrichr result for {database}",
        f"Database: {database}",
        f"Gene count: {len(gene_list)}",
        f"Enriched term count: {len(enrichment_result[database])}",
        f"Top {top_n} terms:"
    ]
    
    for i, term in enumerate(terms, 1):
        name = term[1]
        p_value = term[2]
        genes = term[5]  
        result_lines.append(f"{i}. **{name}**")
        result_lines.append(f"   - P-value: {p_value:.2e}")
        result_lines.append(f"   - gene: {', '.join(genes)}")
    
    return "\n".join(result_lines)

@mcp.tool()
async def list_databases() -> str:
    """
    List all supported databases for enrichment analysis.
    
    Returns:
        List of supported databases and their descriptions
    """
    lines = ["Supported databases:"]
    for db_id, description in DATABASES.items():
        lines.append(f"- **{db_id}**: {description}")
    return "\n".join(lines)

@mcp.tool()
async def analyze_gene_file(
    file_path: str,
    database: str = "KEGG_2021_Human",
    gene_column: str = None,
    top_n: int = 10
) -> str:
    """
    Analyze a gene file and perform pathway enrichment analysis.
    
    Args:
        file_path: Path to the gene file (supports CSV, TSV, Excel)
        database: Database to use for enrichment
        gene_column: Gene column name, None for auto-detection
        top_n: Number of top results to return
    
    Returns:
        Dictionary containing the enrichment results if successful, None otherwise.
    """
    try:
        genes, metadata = read_gene_list(file_path, gene_column)
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    if len(genes) == 0:
        return "Error: No genes found in the file"
    
    result = await perform_enrichment(genes, database, top_n)
    
    file_info = f"## File Information\n"
    file_info += f"- File: {metadata['file']}\n"
    file_info += f"- Gene column: {metadata['gene_column']}\n"
    file_info += f"- Genes found: {metadata['gene_count']}\n\n"
    
    return file_info + result
    
@mcp.tool()
async def enrichment_with_plot(
    gene_list: list[str],
    database: str = "KEGG_2021_Human",
    top_n: int = 10,
    output_path: str = None
) -> str:
    """
    Perform pathway enrichment analysis and generate a visualization plot.
    
    Args:
        gene_list: List of gene symbols
        database: Database name
        top_n: Number of top results to return/plot
        output_path: Path to save the plot, default is current directory
    
    Returns:
        Enrichment results text and plot path
    """

    submit_result = await submit_gene_list(gene_list)
    if not submit_result:
        return "Error: Failed to submit gene list"
    
    user_list_id = submit_result["userListId"]

    enrichment_result = await get_enrichment(user_list_id, database)
    if not enrichment_result or database not in enrichment_result:
        return f"Error: Failed to get enrichment results for {database}"
    
    terms = enrichment_result[database][:top_n]

    plot_path = create_enrichment_barplot(
        terms,
        title=f"Enrichment Analysis - {database}",
        output_path=output_path
    )
    

    result_lines = [
        f"Enrichment Analysis Results",
        f"Database: {database}",
        f"Input genes: {len(gene_list)}",
        f"Enriched terms: {len(enrichment_result[database])}",
        f"Plot saved to: {plot_path}",
        f"\nTop {top_n} Enriched Terms:\n"
    ]
    
    for i, term in enumerate(terms, 1):
        name = term[1]
        p_value = term[2]
        genes = term[5]
        result_lines.append(f"{i}. {name}")
        result_lines.append(f"P-value: {p_value:.2e}")
        result_lines.append(f"Genes: {', '.join(genes)}")
    
    return "\n".join(result_lines)

@mcp.tool()
async def explain_mechanism(
    gene_a: str,
    gene_b: str,
    species: int = 9606
) -> str:
    """
    Explain the potential interaction mechanism between two genes.
    
    Args:
        gene_a: First gene symbol (e.g., TP53)
        gene_b: Second gene symbol (e.g., MDM2)
        species: NCBI taxonomy ID (9606 for Human, 10090 for Mouse)
    
    Returns:
        Detailed interaction information between the two genes
    """
    # Get interaction data
    interactions = await get_interaction(gene_a, gene_b, species)
    
    if not interactions:
        return f"No interaction data found between {gene_a} and {gene_b}"
    
    # Find the specific interaction between gene_a and gene_b
    target_interaction = None
    for item in interactions:
        if (item.get("preferredName_A") == gene_a.upper() and 
            item.get("preferredName_B") == gene_b.upper()) or \
           (item.get("preferredName_A") == gene_b.upper() and 
            item.get("preferredName_B") == gene_a.upper()):
            target_interaction = item
            break
    
    if not target_interaction:
        return f"No direct interaction found between {gene_a} and {gene_b}"
    
    # Format the result
    score = target_interaction.get("score", 0)
    
    result_lines = [
        f"## Interaction: {gene_a} ↔ {gene_b}",
        f"",
        f"### Combined Score: {format_score(score)}",
        f"",
        f"### Evidence Channels:",
    ]
    
    # Evidence scores
    evidence = {
        "nscore": "Gene Neighborhood",
        "fscore": "Gene Fusion", 
        "pscore": "Phylogenetic Profiles",
        "ascore": "Co-expression",
        "escore": "Experimental",
        "dscore": "Database",
        "tscore": "Text Mining"
    }
    
    for key, name in evidence.items():
        if key in target_interaction:
            ev_score = target_interaction[key]
            if ev_score > 0:
                result_lines.append(f"- **{name}**: {ev_score:.3f}")
    
    result_lines.append(f"")
    result_lines.append(f"### Interpretation")
    
    if score >= 0.9:
        result_lines.append(f"These genes have a **very strong** interaction with highest confidence.")
    elif score >= 0.7:
        result_lines.append(f"These genes have a **strong** interaction with high confidence.")
    elif score >= 0.4:
        result_lines.append(f"These genes have a **moderate** interaction with medium confidence.")
    else:
        result_lines.append(f"These genes have a **weak** or poorly characterized interaction.")
    
    return "\n".join(result_lines)


@mcp.tool()
async def get_gene_partners(
    gene: str,
    species: int = 9606,
    limit: int = 10
) -> str:
    """
    Get the top interaction partners for a gene.
    
    Args:
        gene: Gene symbol (e.g., TP53)
        species: NCBI taxonomy ID (9606 for Human)
        limit: Number of partners to return (max 50)
    
    Returns:
        List of top interaction partners with scores
    """
    partners = await get_interaction_partners(gene, species, limit)
    
    if not partners:
        return f"No interaction partners found for {gene}"
    
    result_lines = [
        f"## Top {len(partners)} Interaction Partners for {gene.upper()}",
        f""
    ]
    
    for i, p in enumerate(partners, 1):
        partner_name = p.get("preferredName_B", p.get("stringId_B", "Unknown"))
        score = p.get("score", 0)
        result_lines.append(f"{i}. **{partner_name}** - {format_score(score)}")
    
    return "\n".join(result_lines)




def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()