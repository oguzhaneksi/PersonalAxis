from typing import Dict

def safe_get_text(prop: Dict) -> str:
    """
    Safely extract text from a Notion property.
    Supports title, rich_text, select, multi_select, number, date, and formula types.
    """
    try:
        p_type = prop.get("type")
        if not p_type:
            return ""
            
        if p_type == "title":
            return prop["title"][0]["plain_text"] if prop["title"] else ""
        if p_type == "rich_text":
            return prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
        if p_type == "select":
            return prop["select"]["name"] if prop["select"] else ""
        if p_type == "multi_select":
            return ", ".join([opt["name"] for opt in prop["multi_select"]])
        if p_type == "number":
            return str(prop["number"]) if prop["number"] is not None else "0"
        if p_type == "date":
            return prop["date"]["start"] if prop["date"] else ""
        if p_type == "formula":
            formula_data = prop.get("formula", {})
            f_type = formula_data.get("type")
            if f_type:
                return str(formula_data.get(f_type, ""))
        return ""
    except (KeyError, IndexError, AttributeError):
        return ""
