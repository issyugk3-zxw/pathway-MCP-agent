import httpx

ENRICHR_URL = "https://maayanlab.cloud/Enrichr"

async def submit_gene_list(genes: list[str]) -> dict | None :
    """
    Submit a gene list to Enrichr.
    
    Args:
        genes: List of gene symbols.
    
    Returns:
        Dictionary containing the user list ID if successful, None otherwise.
    """
    url = f"{ENRICHR_URL}/addList"
    genes_str = "\n".join(genes)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                files={"list": (None, genes_str)},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None

async def get_enrichment(user_list_id: int, database: str = "KEGG_2021_Human") -> dict | None:
    """
    Get enrichment results from Enrichr.
    
    Args:
        user_list_id: ID of the user list.
        database: Database to use for enrichment.
    
    Returns:
        Dictionary containing the enrichment results if successful, None otherwise.
    """
    url = f"{ENRICHR_URL}/enrich"
    params = {"userListId": user_list_id, "backgroundType": database}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=60.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None
