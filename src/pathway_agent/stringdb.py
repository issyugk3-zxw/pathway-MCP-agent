import httpx

STRING_API_URL = "https://string-db.org/api"


async def get_interaction(
    gene_a: str,
    gene_b: str,
    species: int = 9606  # Human
) -> dict | None:
    """
    Query the interaction relationship between two genes.
    
    Args:
        gene_a: The first gene symbol
        gene_b: The second gene symbol
        species: Species NCBI taxonomy ID (9606 = Human)
    
    Returns:
        Interaction information dictionary
    """
    url = f"{STRING_API_URL}/json/network"
    
    params = {
        "identifiers": f"{gene_a}%0d{gene_b}",  # %0d = newline separator
        "species": species,
        "caller_identity": "pathway-mcp-agent"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


async def get_interaction_partners(
    gene: str,
    species: int = 9606,
    limit: int = 10
) -> list | None:
    """
    Get the interaction partners of a gene.
    
    Args:
        gene: Gene symbol
        species: Species NCBI taxonomy ID
        limit: Number of interaction partners to return
    
    Returns:
        Interaction partners list
    """
    url = f"{STRING_API_URL}/json/interaction_partners"
    
    params = {
        "identifiers": gene,
        "species": species,
        "limit": limit,
        "caller_identity": "pathway-mcp-agent"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


async def get_functional_annotation(
    genes: list[str],
    species: int = 9606
) -> list | None:
    """
    Get the functional annotation of genes.
    
    Args:
        genes: List of gene symbols
        species: Species NCBI taxonomy ID
    
    Returns:
        Functional annotation list
    """
    url = f"{STRING_API_URL}/json/functional_annotation"
    
    params = {
        "identifiers": "%0d".join(genes),
        "species": species,
        "caller_identity": "pathway-mcp-agent"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None


def format_score(score: float) -> str:
    """Format the interaction score into a readable description."""
    if score >= 0.9:
        return f"{score:.3f} (highest confidence)"
    elif score >= 0.7:
        return f"{score:.3f} (high confidence)"
    elif score >= 0.4:
        return f"{score:.3f} (medium confidence)"
    else:
        return f"{score:.3f} (low confidence)"