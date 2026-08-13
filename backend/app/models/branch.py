"""Branch model for multi-branch POS support.

Provides CRUD operations for branch locations and user-branch assignments.
Each user can be assigned to a single branch for multi-location tracking.
"""
from mysql.connector import MySQLConnection
from typing import List, Dict, Optional


def create_branch(
    conn: MySQLConnection,
    name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    created_by: Optional[int] = None,
) -> int:
    """Create a new branch location for multi-branch POS support."""
    cursor = conn.cursor()
    query = """
        INSERT INTO branches (name, address, phone, email, created_by)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, address, phone, email, created_by))
    conn.commit()
    branch_id = cursor.lastrowid
    cursor.close()
    return branch_id


def get_all_branches(conn: MySQLConnection) -> List[Dict]:
    """Fetch all active branches."""
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM branches WHERE is_active = TRUE ORDER BY name"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results


def get_branch_by_id(conn: MySQLConnection, branch_id: int) -> Optional[Dict]:
    """Fetch a single branch by its ID."""
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM branches WHERE id = %s"
    cursor.execute(query, (branch_id,))
    result = cursor.fetchone()
    cursor.close()
    return result


def update_branch(
    conn: MySQLConnection,
    branch_id: int,
    update_data: Dict,
) -> bool:
    """Update an existing branch's details."""
    fields = []
    values = []
    for key, value in update_data.items():
        if value is not None and key in ["name", "address", "phone", "email", "is_active"]:
            fields.append(f"{key} = %s")
            values.append(value)
    if not fields:
        return False
    values.append(branch_id)
    query = f"UPDATE branches SET {', '.join(fields)} WHERE id = %s"
    cursor = conn.cursor()
    cursor.execute(query, tuple(values))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected > 0


def delete_branch(conn: MySQLConnection, branch_id: int) -> bool:
    """Soft delete a branch by deactivating it."""
    cursor = conn.cursor()
    query = "UPDATE branches SET is_active = FALSE WHERE id = %s"
    cursor.execute(query, (branch_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected > 0


def assign_branch_to_user(
    conn: MySQLConnection,
    user_id: int,
    branch_id: int,
) -> bool:
    """Assign a user to a specific branch."""
    cursor = conn.cursor()
    # Remove existing assignments for this user (single branch per user)
    cursor.execute("DELETE FROM user_branches WHERE user_id = %s", (user_id,))
    cursor.execute(
        "INSERT INTO user_branches (user_id, branch_id) VALUES (%s, %s)",
        (user_id, branch_id),
    )
    conn.commit()
    cursor.close()
    return True


def get_user_branch(conn: MySQLConnection, user_id: int) -> Optional[Dict]:
    """Get the branch assigned to a user."""
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT b.* FROM branches b
        JOIN user_branches ub ON b.id = ub.branch_id
        WHERE ub.user_id = %s AND b.is_active = TRUE
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    return result