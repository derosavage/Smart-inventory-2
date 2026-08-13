from mysql.connector import MySQLConnection
from typing import List, Dict, Optional
from datetime import date, timedelta


def get_sales_report(
    conn: MySQLConnection,
    from_date: date,
    to_date: date,
    group_by: str = "day"
) -> List[Dict]:
    """Get sales data grouped by day/week/month."""
    cursor = conn.cursor(dictionary=True)
    
    # Determine SQL grouping
    if group_by == "day":
        group_expr = "transaction_date"
        order = "transaction_date"
    elif group_by == "week":
        group_expr = "DATE_SUB(transaction_date, INTERVAL WEEKDAY(transaction_date) DAY)"
        order = "week_start"
    else:  # month
        group_expr = "DATE_FORMAT(transaction_date, '%Y-%m-01')"
        order = "month_start"
    
    query = f"""
        SELECT
            {group_expr} AS period,
            COUNT(DISTINCT id) AS transaction_count,
            COALESCE(SUM(total_items_sold), 0) AS items_sold,
            COALESCE(SUM(total_revenue), 0) AS revenue,
            COALESCE(SUM(tax_collected), 0) AS tax_collected
        FROM daily_sales_summary
        WHERE transaction_date BETWEEN %s AND %s
        GROUP BY period
        ORDER BY {order}
    """
    cursor.execute(query, (from_date, to_date))
    results = cursor.fetchall()
    cursor.close()
    return results


def get_stock_movement_report(
    conn: MySQLConnection,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    product_sku: Optional[str] = None,
    movement_type: Optional[str] = None,
    limit: int = 1000
) -> List[Dict]:
    """Get stock movements with optional filters."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT
            sm.id,
            sm.created_at AS datetime,
            p.sku AS product_sku,
            p.name AS product_name,
            mt.name AS movement_type,
            sm.quantity,
            sm.previous_quantity,
            sm.new_quantity,
            sm.reason,
            u.username AS performed_by
        FROM stock_movements sm
        JOIN products p ON sm.product_sku = p.sku
        JOIN movement_types mt ON sm.movement_type_id = mt.id
        LEFT JOIN users u ON sm.created_by = u.id
        WHERE 1=1
    """
    params = []
    if from_date:
        query += " AND DATE(sm.created_at) >= %s"
        params.append(from_date)
    if to_date:
        query += " AND DATE(sm.created_at) <= %s"
        params.append(to_date)
    if product_sku:
        query += " AND p.sku = %s"
        params.append(product_sku)
    if movement_type:
        query += " AND mt.name = %s"
        params.append(movement_type)
    query += " ORDER BY sm.created_at DESC LIMIT %s"
    params.append(limit)
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    return results


def get_product_performance_report(
    conn: MySQLConnection,
    sort_by: str = "total_sold_30d",
    limit: int = 50
) -> List[Dict]:
    """Get product performance from the product_performance view."""
    cursor = conn.cursor(dictionary=True)
    
    # Map sort_by to column
    sort_col = {
        "total_sold_30d": "total_sold_30d DESC",
        "avg_daily_sales": "avg_daily_sales DESC",
        "stock": "quantity_in_stock DESC",
        "slow_movers": "total_sold_30d ASC",
        "name": "name"
    }.get(sort_by, "total_sold_30d DESC")
    
    query = f"""
        SELECT
            sku,
            name,
            category_name AS category,
            quantity_in_stock AS current_stock,
            total_sold_30d,
            avg_daily_sales,
            CASE
                WHEN quantity_in_stock > 0 THEN ROUND(total_sold_30d / quantity_in_stock, 2)
                ELSE NULL
            END AS turnover_rate,
            status
        FROM product_performance
        ORDER BY {sort_col}
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    cursor.close()
    return results


def get_distinct_movement_types(conn: MySQLConnection) -> List[str]:
    """Get all distinct movement type names for filter dropdown."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM movement_types ORDER BY name")
    results = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return results


def get_distinct_product_skus(conn: MySQLConnection) -> List[Dict]:
    """Get product SKUs and names for filter dropdown."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT sku, name FROM products WHERE is_active = TRUE ORDER BY name")
    results = cursor.fetchall()
    cursor.close()
    return results


def get_profit_loss_report(
    conn: MySQLConnection,
    from_date: date,
    to_date: date,
    branch_id: Optional[int] = None,
) -> Dict:
    """Calculate profit and loss for a date range.

    Returns total revenue, total cost of goods sold, gross profit,
    operating expenses, and net profit.
    """
    cursor = conn.cursor(dictionary=True)

    # Revenue and COGS from sales
    revenue_query = """
        SELECT
            COALESCE(SUM(st.total_amount), 0) AS total_revenue,
            COALESCE(SUM(sl.quantity * p.cost_price), 0) AS total_cogs,
            COALESCE(SUM(sl.quantity), 0) AS total_items_sold,
            COALESCE(SUM(st.tax_amount), 0) AS total_tax_collected
        FROM sale_transactions st
        JOIN sale_line_items sl ON st.id = sl.transaction_id
        JOIN products p ON sl.product_sku = p.sku
        WHERE st.transaction_date BETWEEN %s AND %s
    """
    params = [from_date, to_date]
    if branch_id:
        revenue_query += " AND st.branch_id = %s"
        params.append(branch_id)

    cursor.execute(revenue_query, tuple(params))
    financials = cursor.fetchone()

    # Operating expenses from stock adjustments
    expense_query = """
        SELECT
            COALESCE(SUM(sm.quantity * p.cost_price), 0) AS total_adjustment_cost
        FROM stock_movements sm
        JOIN products p ON sm.product_sku = p.sku
        JOIN movement_types mt ON sm.movement_type_id = mt.id
        WHERE mt.name IN ('adjustment', 'damage', 'return')
        AND DATE(sm.created_at) BETWEEN %s AND %s
    """
    cursor.execute(expense_query, (from_date, to_date))
    expenses = cursor.fetchone()

    cursor.close()

    total_revenue = financials["total_revenue"] if financials else 0
    total_cogs = financials["total_cogs"] if financials else 0
    gross_profit = total_revenue - total_cogs
    total_expenses = expenses["total_adjustment_cost"] if expenses else 0
    net_profit = gross_profit - total_expenses

    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "total_revenue": float(total_revenue),
        "total_cogs": float(total_cogs),
        "gross_profit": float(gross_profit),
        "total_expenses": float(total_expenses),
        "net_profit": float(net_profit),
        "total_items_sold": financials["total_items_sold"] if financials else 0,
        "total_tax_collected": float(financials["total_tax_collected"]) if financials else 0,
    }


def get_daily_business_report(
    conn: MySQLConnection,
    target_date: date,
    branch_id: Optional[int] = None,
) -> Dict:
    """Get a comprehensive daily business snapshot for real-time tracking."""
    cursor = conn.cursor(dictionary=True)

    # Sales summary
    sales_query = """
        SELECT
            COUNT(DISTINCT id) AS total_transactions,
            COUNT(DISTINCT sli.product_sku) AS unique_products,
            COALESCE(SUM(sl.quantity), 0) AS total_items_sold,
            COALESCE(SUM(st.total_amount), 0) AS total_revenue,
            COALESCE(SUM(st.tax_amount), 0) AS total_tax
        FROM sale_transactions st
        JOIN sale_line_items sli ON st.id = sli.transaction_id
        WHERE DATE(st.transaction_date) = DATE(%s)
    """
    params = [target_date]
    if branch_id:
        sales_query += " AND st.branch_id = %s"
        params.append(branch_id)
    cursor.execute(sales_query, tuple(params))
    sales_summary = cursor.fetchone()

    # Top selling product
    top_product_query = """
        SELECT p.name, SUM(sl.quantity) AS qty_sold, SUM(sl.quantity * sl.unit_price) AS revenue
        FROM sale_line_items sl
        JOIN products p ON sl.product_sku = p.sku
        JOIN sale_transactions st ON sl.transaction_id = st.id
        WHERE DATE(st.transaction_date) = DATE(%s)
    """
    top_params = [target_date]
    if branch_id:
        top_product_query += " AND st.branch_id = %s"
        top_params.append(branch_id)
    top_product_query += " GROUP BY p.name ORDER BY qty_sold DESC LIMIT 1"
    cursor.execute(top_product_query, tuple(top_params))
    top_product = cursor.fetchone()

    # Stock movements today
    movements_query = """
        SELECT COUNT(*) AS movement_count,
               COALESCE(SUM(quantity), 0) AS total_moved
        FROM stock_movements sm
        WHERE DATE(sm.created_at) = DATE(%s)
    """
    cursor.execute(movements_query, (target_date,))
    movement_summary = cursor.fetchone()

    # Low stock count
    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE quantity_in_stock <= reorder_threshold AND is_active = TRUE"
    )
    low_stock_count = cursor.fetchone()[0]

    # Out of stock count
    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE quantity_in_stock = 0 AND is_active = TRUE"
    )
    out_of_stock_count = cursor.fetchone()[0]

    cursor.close()

    return {
        "date": str(target_date),
        "sales": sales_summary or {
            "total_transactions": 0, "unique_products": 0,
            "total_items_sold": 0, "total_revenue": 0, "total_tax": 0,
        },
        "top_product": top_product,
        "movements": movement_summary or {"movement_count": 0, "total_moved": 0},
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }