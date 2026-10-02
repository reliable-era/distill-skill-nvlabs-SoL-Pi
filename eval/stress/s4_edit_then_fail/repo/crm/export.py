from crm.names import format_name


def export_csv(contacts):
    """Export contacts as CSV text with header 'name,email'."""
    rows = ["name,email"]
    for c in contacts:
        rows.append(f"{format_name(c['first'], c['last'])},{c['email']}")
    return "\n".join(rows) + "\n"
