# 🧬 Pathway MCP Agent

A Model Context Protocol (MCP) server for gene enrichment analysis and protein-protein interaction queries.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)

## Features

- 🔬 **Gene Enrichment Analysis** - Query Enrichr API for pathway enrichment
- 🔗 **Protein Interaction** - Query STRING-db for gene interactions
- 📊 **Visualization** - Generate publication-ready bar plots
- 📁 **File Support** - Read gene lists from CSV, TSV, Excel files
- 🤖 **MCP Compatible** - Works with Claude Desktop, VS Code, and other MCP clients

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/pathway-mcp-agent.git
cd pathway-mcp-agent

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Quick Start

### Run the MCP Server

```bash
uv run pathway-agent
```

### Configure Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "pathway-agent": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/pathway-mcp-agent",
        "run",
        "pathway-agent"
      ]
    }
  }
}
```

## Available Tools

### `perform_enrichment`

Perform pathway enrichment analysis on a gene list.

```
Input: gene_list=["TP53", "BRCA1", "EGFR"], database="KEGG_2021_Human"
Output: Enriched pathways with p-values and gene overlaps
```

### `enrichment_with_plot`

Perform enrichment analysis and generate a visualization.

```
Input: gene_list=["TP53", "BRCA1"], database="KEGG_2021_Human", output_path="./plot.png"
Output: Enrichment results + saved bar plot
```

### `explain_mechanism`

Explain the interaction mechanism between two genes using STRING-db.

```
Input: gene_a="TP53", gene_b="MDM2"
Output: Interaction score, evidence channels, interpretation
```

### `get_gene_partners`

Get top interaction partners for a gene.

```
Input: gene="TP53", limit=10
Output: Top 10 interaction partners with confidence scores
```

### `analyze_gene_file`

Read genes from a file and perform enrichment analysis.

```
Input: file_path="./genes.csv", database="KEGG_2021_Human"
Output: File info + enrichment results
```

### `list_databases`

List all supported enrichment databases.

## Supported Databases

| Database | Description |
|----------|-------------|
| KEGG_2021_Human | KEGG Pathways |
| GO_Biological_Process_2021 | Gene Ontology BP |
| GO_Cellular_Component_2021 | Gene Ontology CC |
| GO_Molecular_Function_2021 | Gene Ontology MF |
| MSigDB_Hallmark_2020 | MSigDB Hallmark Gene Sets |

## Example Output

### Enrichment Analysis

```
Enrichr result for KEGG_2021_Human
Database: KEGG_2021_Human
Gene count: 5
Enriched term count: 110

Top 5 terms:
1. **Breast cancer**
   - P-value: 2.00e-11
   - gene: MYC, KRAS, BRCA1, TP53, EGFR
```

### Gene Interaction

```
## Interaction: TP53 ↔ MDM2

### Combined Score: 0.999 (highest confidence)

### Evidence Channels:
- Experimental: 0.999
- Database: 0.900
- Text Mining: 0.999
```

## API References

- [Enrichr](https://maayanlab.cloud/Enrichr/) - Ma'ayan Lab
- [STRING-db](https://string-db.org/) - Protein-Protein Interaction Database

```
