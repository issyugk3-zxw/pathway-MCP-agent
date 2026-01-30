import pandas as pd
from pathlib import Path


def read_gene_list(
    file_path: str,
    gene_column: str = None,
    sheet_name: str | int = 0
) -> tuple[list[str], dict]:
    """
    Read gene list from file.
    
    Args:
        file_path: File path (supports CSV, TSV, Excel)
        gene_column: Gene column name, None for auto-detection
        sheet_name: Excel sheet name or index
    
    Returns:
        (Gene list, Metadata dictionary)
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    

    suffix = path.suffix.lower()
    
    if suffix == '.csv':
        df = pd.read_csv(file_path)
    elif suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    elif suffix in ['.tsv', '.txt']:
        df = pd.read_csv(file_path, sep='\t')
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    if gene_column is None:
        gene_column = detect_gene_column(df)
        if gene_column is None:
            gene_column = df.columns[0]     
    
    if gene_column not in df.columns:
        raise ValueError(f"Column '{gene_column}' does not exist. Available columns: {list(df.columns)}")
    
    genes = df[gene_column].dropna().astype(str).str.strip().str.upper().tolist()
    genes = [g for g in genes if g and g != 'NAN']
    
    metadata = {
        "file": str(path.name),
        "total_rows": len(df),
        "gene_column": gene_column,
        "gene_count": len(genes),
        "columns": list(df.columns)
    }
    
    return genes, metadata


def detect_gene_column(df: pd.DataFrame) -> str | None:
    """Auto-detect gene column."""      
    common_names = [
        'gene', 'genes', 'gene_symbol', 'gene_name', 'symbol',
        'Gene', 'Genes', 'Gene_Symbol', 'Gene_Name', 'Symbol',
        'GENE', 'GENES', 'GENE_SYMBOL', 'GENE_NAME', 'SYMBOL',
        'geneid', 'gene_id', 'GeneID', 'Gene_ID'
    ]
    
    for col in df.columns:
        if col in common_names or col.lower() in [n.lower() for n in common_names]:
            return col
    
    return None