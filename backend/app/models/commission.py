from mysql.connector import MySQLConnection
from typing import List, Dict, Optional
from datetime import datetime, date


def create_commission_rule(
    conn: MySQLConnection,
    name: str,
    commission_type: str,
    rate: float,
    target_type: str,
    target_id: Optional[int] = None,
    created_by: Optional[int] = None,
) -> int:
    """Create a new commission rule (percentage-based for staff or products)."""
    cursor = conn.cursor()
    query = """
        INSERT INTO commission_rules (name, commission_type, rate, target_type, target_id, created_by)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, commission_type, rate, target_type, target_id, created_by))
    conn.commit()
    rule_id = cursor.lastrowid
    cursor.close()
    return rule_id


def get_all_commission_rules(conn: MySQLConnection) -> List[Dict]:
    """Fetch all commission rules with optional target details."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT cr.*,
               p.name AS product_name,
               u.username AS staff_name
        FROM commission_rules cr
        LEFT JOIN products p ON cr.target_id = p.id AND cr.target_type = 'product'
        LEFT JOIN users u ON cr.target_id = u.id AND cr.target_type = 'staff'
        WHERE cr.is_active = TRUE
        ORDER BY cr.created_at DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results


def get_commission_rule_by_id(
    conn: MySQLConnection,
    rule_id: int,
) -> Optional[Dict]:
    """Fetch a single commission rule by ID."""
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM commission_rules WHERE id = %s"
    cursor.execute(query, (rule_id,))
    result = cursor.fetchone()
    cursor.close()
    return result


def update_commission_rule(
    conn: MySQLConnection,
    rule_id: int,
    update_data: Dict,
) -> bool:
    """Update an existing commission rule."""
    fields = []
    values = []
    for key, value in update_data.items():
        if value is not None and key in ["name", "rate", "target_type", "target_id", "is_active"]:
            fields.append(f"{key} = %s")
            values.append(value)
    if not fields:
        return False
    values.append(rule_id)
    query = f"UPDATE commission_rules SET {', '.join(fields)} WHERE id = %s"
    cursor = conn.cursor()
    cursor.execute(query, tuple(values))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected > 0


def delete_commission_rule(conn: MySQLConnection, rule_id: int) -> bool:
    """Deactivate a commission rule (soft delete)."""
    cursor = conn.cursor()
    query = "UPDATE commission_rules SET is_active = FALSE WHERE id = %s"
    cursor.execute(query, (rule_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected > 0


def get_staff_commission_summary(
    conn: MySQLConnection,
    user_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Dict:
    """Get total commission earned by a staff member for a date range."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT
            COALESCE(SUM(sl.quantity * sl.unit_price * cr.rate / 100), 0) AS total_commission,
            COALESCE(SUM(sl.quantity), 0) AS total_items_sold,
            COALESCE(SUM(sl.quantity * sl.unit_price), 0) AS total_sales
        FROM sale_line_items sl
        JOIN sale_transactions st ON sl.transaction_id = st.id
        JOIN commission_rules cr ON cr.target_type = 'staff' AND cr.target_id = st.user_id
        WHERE st.user_id = %s
        AND cr.is_active = TRUE
    """
    params = [user_id]
    if from_date:
        query += " AND st.transaction_date >= %s"
        params.append(from_date)
    if to_date:
        query += " AND st.transaction_date <= %s"
        params.append(to_date)
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    cursor.close()
    return result or {"total_commission": 0, "total_items_sold": 0, "total_sales": 0}


def get_product_commission_summary(
    conn: MySQLConnection,
    product_sku: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> List[Dict]:
    """Get commission summary per product for reporting."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT
            p.sku,
            p.name AS product_name,
            COALESCE(SUM(sl.quantity), 0) AS total_quantity_sold,
            COALESCE(SUM(sl.quantity * sl.unit_price), 0) AS total_revenue,
            COALESCE(SUM(sl.quantity * sl.unit_price * cr.rate / 100), 0) AS total_commission
        FROM sale_line_items sl
        JOIN sale_transactions st ON sl.transaction_id = st.id
        JOIN products p ON sl.product_sku = p.sku
        JOIN commission_rules cr ON cr.target_type = 'product' AND cr.target_id = p.id
        WHERE cr.is_active = TRUE
    """
    params = []
    if product_sku:
        query += " AND p.sku = %s"
        params.append(product_sku)
    if from_date:
        query += " AND st.transaction_date >= %s"
        params.append(from_date)
    if to_date:
        query += " AND st.transaction_date <= %s"
        params.append(to_date)
    query += " GROUP BY p.sku, p.name ORDER BY total_commission DESC"
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    return results