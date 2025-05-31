import re

def validate_full_name_usage(sql_query: str) -> bool:
    """
    Validates that the SQL query returns full name using CONCAT or an alias like 'full_name',
    and does not return 'first_name' and 'last_name' as separate columns.
    Raises ValueError if the validation fails.
    """
    # Normalize and strip formatting artifacts
    query = sql_query.strip().strip("`").strip().lower()

    # Extract SELECT clause (between SELECT and FROM)
    match = re.search(r"select\s+(.*?)\s+from", query, re.DOTALL)
    if not match:
        raise ValueError("Invalid SQL: Could not parse SELECT clause.")

    select_clause = match.group(1).strip()

    # Check for good case: CONCAT or alias for full name
    if "concat(" in select_clause or "full_name" in select_clause:
        return True

    # Check for bad case: both first_name and last_name used separately
    has_first_name = re.search(r"\bfirst_name\b", select_clause)
    has_last_name = re.search(r"\blast_name\b", select_clause)

    if has_first_name and has_last_name:
        raise ValueError(
            "Invalid SQL: Query should return full name using CONCAT(first_name, ' ', last_name) or as 'full_name'."
        )

    # If none of the above matched, assume valid
    return True