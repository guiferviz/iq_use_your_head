import yaml


def generate_n_queens_yaml(n):
    constraints = {}
    candidates = {}

    # Define constraints with descriptions
    for i in range(n):
        constraints[f"R{i+1}"] = f"Row {i+1} has a queen."
        constraints[f"C{i+1}"] = f"Column {i+1} has a queen."

    for i in range(2 * n - 1):
        constraints[f"D{i}"] = f"Major diagonal {i} has a queen."
        constraints[f"A{i}"] = f"Minor diagonal {i} has a queen."

    # Define candidates for placing queens
    for i in range(n):
        for j in range(n):
            row_constraint = f"R{i+1}"
            col_constraint = f"C{j+1}"
            major_diag_constraint = f"D{i-j+n-1}"
            minor_diag_constraint = f"A{i+j}"
            candidate_key = f"{row_constraint} {col_constraint} {major_diag_constraint} {minor_diag_constraint}"
            candidates[candidate_key] = f"Queen at ({i}, {j})"

    # Add candidates for "at most one queen" on each diagonal
    for i in range(2 * n - 1):
        major_diag_constraint = f"D{i}"
        minor_diag_constraint = f"A{i}"
        candidates[major_diag_constraint] = (
            f"No queen needs to be placed in major diagonal {i}"
        )
        candidates[minor_diag_constraint] = (
            f"No queen needs to be placed in minor diagonal {i}"
        )

    # Create dictionary for YAML
    data = {"constraints": constraints, "candidates": candidates}

    # Convert to YAML
    yaml_data = yaml.dump(data, sort_keys=False)
    return yaml_data


# Example usage
n = 14  # Change n to generate for different board sizes
yaml_output = generate_n_queens_yaml(n)
print(yaml_output)
