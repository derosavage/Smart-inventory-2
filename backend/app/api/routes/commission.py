from fastapi import APIRouter, Depends, HTTPException, Query, status
from mysql.connector import MySQLConnection
from typing import List, Optional
from datetime import date

from ...schemas.admin import (
    CommissionRuleCreate,
    CommissionRuleResponse,
    CommissionRuleUpdate,
)
from ...schemas.report import ProfitLossReport
from ...models import commission as commission_model
from ...models import report as report_model
from ...core.database import get_db
from ...api.dependencies import get_current_active_manager

router = APIRouter(prefix="/commissions", tags=["Commissions"])


# ---------- Commission Rules ----------
@router.get("/rules", response_model=List[CommissionRuleResponse])
def get_commission_rules(
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """List all active commission rules."""
    return commission_model.get_all_commission_rules(conn)


@router.post("/rules", response_model=CommissionRuleResponse, status_code=status.HTTP_201_CREATED)
def create_commission_rule(
    rule: CommissionRuleCreate,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Create a new commission rule."""
    rule_id = commission_model.create_commission_rule(
        conn,
        name=rule.name,
        commission_type=rule.commission_type,
        rate=rule.rate,
        target_type=rule.target_type,
        target_id=rule.target_id,
        created_by=current_user["id"],
    )
    return commission_model.get_commission_rule_by_id(conn, rule_id)


@router.get("/rules/{rule_id}", response_model=CommissionRuleResponse)
def get_commission_rule(
    rule_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Get a single commission rule."""
    rule = commission_model.get_commission_rule_by_id(conn, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Commission rule not found")
    return rule


@router.put("/rules/{rule_id}", response_model=CommissionRuleResponse)
def update_commission_rule(
    rule_id: int,
    rule: CommissionRuleUpdate,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Update an existing commission rule."""
    success = commission_model.update_commission_rule(
        conn, rule_id, rule.model_dump(exclude_unset=True)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Commission rule not found")
    return commission_model.get_commission_rule_by_id(conn, rule_id)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_commission_rule(
    rule_id: int,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Deactivate a commission rule (soft delete)."""
    success = commission_model.delete_commission_rule(conn, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Commission rule not found")
    return None


# ---------- Commission Reports ----------
@router.get("/staff/{user_id}/summary")
def get_staff_commission_summary(
    user_id: int,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Get commission summary for a staff member."""
    return commission_model.get_staff_commission_summary(conn, user_id, from_date, to_date)


@router.get("/products/summary")
def get_product_commission_summary(
    product_sku: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Get commission summary per product."""
    return commission_model.get_product_commission_summary(
        conn, product_sku, from_date, to_date
    )


# ---------- Profit & Loss ----------
@router.get("/profit-loss", response_model=ProfitLossReport)
def get_profit_loss_report(
    from_date: date,
    to_date: date,
    branch_id: Optional[int] = Query(None, description="Filter by branch"),
    conn: MySQLConnection = Depends(get_db),
    current_user = Depends(get_current_active_manager),
):
    """Generate a profit and loss report for a date range."""
    if from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be before to_date")
    return report_model.get_profit_loss_report(conn, from_date, to_date, branch_id)