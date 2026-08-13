from mysql.connector import MySQLConnection
from typing import List, Dict, Optional
from datetime import datetime
import json


def create_sale(
    conn: MySQLConnection,
    transaction_number: str,
    user_id: int,
    transaction_date: datetime,
    items: List[Dict],
    branch_id: Optional[int] = None,
    tax_type: str = "standard",
    tax_amount: float = 0.0,
    notes: Optional[str] = None,
) -> int:
    """Call the ProcessSale stored procedure.

    Args:
        conn: Database connection
        transaction_number: Unique receipt/invoice number
        user_id: ID of the cashier processing the sale
        transaction_date: Date of the transaction
        items: List of sale items with sku, quantity, unit_price
        branch_id: Branch ID for multi-branch support
        tax_type: 'standard' (VAT) or 'non-tax' (KRA exempt)
        tax_amount: Total tax charged for the transaction
        notes: Optional notes for the receipt (e.g., ETR number, payment method)
    """
    cursor = conn.cursor()

    # Convert items list to JSON string as expected by the procedure
    items_json = json.dumps(items)

    cursor.callproc(
        "ProcessSale",
        (transaction_number, user_id, transaction_date, items_json),
    )

    # Fetch the result (transaction_id)
    result = cursor.stored_results()
    transaction_id = None
    for res in result:
        row = res.fetchone()
        if row:
            transaction_id = row[0]

    # Update the transaction with tax and branch info
    if transaction_id:
        cursor.execute(
            """
            UPDATE sale_transactions
            SET tax_type = %s, tax_amount = %s, branch_id = %s, notes = %s
            WHERE id = %s
            """,
            (tax_type, tax_amount, branch_id, notes, transaction_id),
        )

    conn.commit()
    cursor.close()
    return transaction_id

def get_transaction_by_id(conn: MySQLConnection, transaction_id: int) -> Optional[Dict]:
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            st.*,
            u.username
        FROM sale_transactions st
        JOIN users u ON st.user_id = u.id
        WHERE st.id = %s
    """
    cursor.execute(query, (transaction_id,))
    transaction = cursor.fetchone()
    cursor.close()
    return transaction

def get_transaction_items(conn: MySQLConnection, transaction_id: int) -> List[Dict]:
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            sli.*,
            p.name as product_name
        FROM sale_line_items sli
        JOIN products p ON sli.product_sku = p.sku
        WHERE sli.transaction_id = %s
    """
    cursor.execute(query, (transaction_id,))
    items = cursor.fetchall()
    cursor.close()
    return items

def get_transactions(
    conn: MySQLConnection,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]:
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            st.id,
            st.transaction_number,
            st.user_id,
            u.username,
            st.total_amount,
            st.transaction_date,
            st.created_at
        FROM sale_transactions st
        JOIN users u ON st.user_id = u.id
        WHERE 1=1
    """
    params = []
    if from_date:
        query += " AND st.transaction_date >= %s"
        params.append(from_date)
    if to_date:
        query += " AND st.transaction_date <= %s"
        params.append(to_date)
    query += " ORDER BY st.transaction_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cursor.execute(query, tuple(params))
    transactions = cursor.fetchall()
    cursor.close()
    return transactions

def get_daily_summary(conn: MySQLConnection, date: datetime) -> Optional[Dict]:
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            COUNT(DISTINCT id) as total_transactions,
            COALESCE(SUM(total_amount), 0) as total_revenue,
            COALESCE(SUM((
                SELECT SUM(quantity) 
                FROM sale_line_items 
                WHERE transaction_id = st.id
            )), 0) as total_items_sold
        FROM sale_transactions st
        WHERE DATE(st.transaction_date) = DATE(%s)
    """
    cursor.execute(query, (date,))
    summary = cursor.fetchone()
    cursor.close()
    return summary