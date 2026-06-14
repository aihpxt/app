"""会员系统API"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime, timedelta

router = APIRouter()

DB_PATH = "data/schools.db"

class MembershipLevel(BaseModel):
    id: int
    name: str
    description: str
    price_monthly: float
    price_quarterly: float
    price_yearly: float
    features: dict

class PaymentRequest(BaseModel):
    user_id: int
    level_id: int
    duration_months: int
    payment_method: str

class UsageCheckRequest(BaseModel):
    user_id: int
    feature_type: str

@router.get("/levels")
async def get_membership_levels():
    """获取所有会员等级"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, price_monthly, price_quarterly, price_yearly, features
            FROM membership_levels
            ORDER BY price_monthly
        ''')
        
        levels = []
        for row in cursor.fetchall():
            import json
            levels.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price_monthly": row[3],
                "price_quarterly": row[4],
                "price_yearly": row[5],
                "features": json.loads(row[6]) if row[6] else {}
            })
        
        conn.close()
        return {"success": True, "data": levels}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_membership(user_id: int):
    """获取用户会员信息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT um.level_id, ml.name, ml.features, um.start_date, um.end_date, um.status
            FROM user_memberships um
            JOIN membership_levels ml ON um.level_id = ml.id
            WHERE um.user_id = ? AND um.status = 'active' AND um.end_date >= date('now')
            ORDER BY um.end_date DESC
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            import json
            membership = {
                "level_id": row[0],
                "level_name": row[1],
                "features": json.loads(row[2]) if row[2] else {},
                "start_date": row[3],
                "end_date": row[4],
                "status": row[5]
            }
        else:
            cursor.execute('''
                SELECT id, name, features FROM membership_levels WHERE name = '免费用户'
            ''')
            free_row = cursor.fetchone()
            import json
            membership = {
                "level_id": free_row[0] if free_row else 1,
                "level_name": "免费用户",
                "features": json.loads(free_row[2]) if free_row and free_row[2] else {},
                "start_date": None,
                "end_date": None,
                "status": "free"
            }
        
        conn.close()
        return {"success": True, "data": membership}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-usage")
async def check_usage_limit(request: UsageCheckRequest):
    """检查用户功能使用次数"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取用户会员等级
        cursor.execute('''
            SELECT ml.features
            FROM user_memberships um
            JOIN membership_levels ml ON um.level_id = ml.id
            WHERE um.user_id = ? AND um.status = 'active' AND um.end_date >= date('now')
            ORDER BY um.end_date DESC
            LIMIT 1
        ''', (request.user_id,))
        
        row = cursor.fetchone()
        
        if row:
            import json
            features = json.loads(row[0]) if row[0] else {}
        else:
            cursor.execute("SELECT features FROM membership_levels WHERE name = '免费用户'")
            free_row = cursor.fetchone()
            import json
            features = json.loads(free_row[0]) if free_row and free_row[0] else {}
        
        # 获取功能限制
        feature_config = features.get(request.feature_type, {})
        
        if isinstance(feature_config, bool):
            allowed = feature_config
            remaining = -1 if allowed else 0
        elif isinstance(feature_config, dict):
            daily_limit = feature_config.get('daily_limit', 0)
            if daily_limit == -1:
                allowed = True
                remaining = -1
            else:
                # 检查今日使用次数
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    SELECT usage_count, last_reset FROM usage_records
                    WHERE user_id = ? AND feature_type = ?
                ''', (request.user_id, request.feature_type))
                
                usage_row = cursor.fetchone()
                
                if usage_row and usage_row[1] == today:
                    used = usage_row[0]
                else:
                    used = 0
                    cursor.execute('''
                        INSERT OR REPLACE INTO usage_records (user_id, feature_type, usage_count, last_reset)
                        VALUES (?, ?, 0, ?)
                    ''', (request.user_id, request.feature_type, today))
                    conn.commit()
                
                remaining = daily_limit - used
                allowed = remaining > 0
        else:
            allowed = False
            remaining = 0
        
        conn.close()
        
        return {
            "success": True,
            "data": {
                "allowed": allowed,
                "remaining": remaining,
                "feature": request.feature_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-usage")
async def record_usage(request: UsageCheckRequest):
    """记录功能使用"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT id, usage_count, last_reset FROM usage_records
            WHERE user_id = ? AND feature_type = ?
        ''', (request.user_id, request.feature_type))
        
        row = cursor.fetchone()
        
        if row and row[2] == today:
            new_count = row[1] + 1
            cursor.execute('''
                UPDATE usage_records SET usage_count = ? WHERE id = ?
            ''', (new_count, row[0]))
        else:
            new_count = 1
            cursor.execute('''
                INSERT OR REPLACE INTO usage_records (user_id, feature_type, usage_count, last_reset)
                VALUES (?, ?, 1, ?)
            ''', (request.user_id, request.feature_type, today))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "data": {"count": new_count}}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/purchase")
async def purchase_membership(request: PaymentRequest):
    """购买会员"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取会员等级价格
        cursor.execute('''
            SELECT price_monthly, price_quarterly, price_yearly FROM membership_levels WHERE id = ?
        ''', (request.level_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="会员等级不存在")
        
        # 计算价格
        if request.duration_months == 1:
            amount = row[0]
        elif request.duration_months == 3:
            amount = row[1]
        elif request.duration_months == 12:
            amount = row[2]
        else:
            amount = row[0] * request.duration_months
        
        # 创建支付记录
        cursor.execute('''
            INSERT INTO payments (user_id, amount, payment_method, membership_level, duration_months)
            VALUES (?, ?, ?, ?, ?)
        ''', (request.user_id, amount, request.payment_method, request.level_id, request.duration_months))
        
        payment_id = cursor.lastrowid
        
        # 模拟支付成功（实际应调用支付接口）
        cursor.execute('''
            UPDATE payments SET payment_status = 'success', transaction_id = ?
            WHERE id = ?
        ''', (f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{payment_id}", payment_id))
        
        # 创建会员记录
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=request.duration_months * 30)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO user_memberships (user_id, level_id, start_date, end_date, payment_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (request.user_id, request.level_id, start_date, end_date, str(payment_id)))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "payment_id": payment_id,
                "amount": amount,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
