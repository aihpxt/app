#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""政策信息API路由"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
import sqlite3
import os
from datetime import datetime

router = APIRouter()

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH = os.path.join(BASE_DIR, "sqlite", "data", "unified_school_data.db")


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/policies")
async def get_policies(
    category: Optional[str] = Query(None, description="政策分类"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
) -> Dict[str, Any]:
    """
    获取政策列表
    
    - **category**: 政策分类（招生政策、加分政策、志愿填报等）
    - **keyword**: 关键词搜索
    - **page**: 页码
    - **size**: 每页数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if keyword:
            conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM policies WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        offset = (page - 1) * size
        query_sql = f"""
            SELECT id, title, content, category, publish_date
            FROM policies
            WHERE {where_clause}
            ORDER BY publish_date DESC, id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        
        cursor.execute(query_sql, params)
        rows = cursor.fetchall()
        
        items = [
            {
                "id": row['id'],
                "title": row['title'],
                "content": row['content'],
                "category": row['category'],
                "publish_date": row['publish_date'],
                "source": ""
            }
            for row in rows
        ]
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": (total + size - 1) // size
            },
            "message": ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/policies/categories")
async def get_categories() -> Dict[str, Any]:
    """获取所有政策分类"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM policies 
            GROUP BY category 
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        
        categories = [
            {"name": row['category'], "count": row['count']}
            for row in rows
        ]
        
        return {
            "success": True,
            "data": categories,
            "message": ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/policies/search")
async def search_policies(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="政策分类"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
) -> Dict[str, Any]:
    """
    搜索政策
    
    - **q**: 搜索关键词
    - **category**: 政策分类
    - **limit**: 返回数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        conditions = ["(title LIKE ? OR content LIKE ?)"]
        params = [f"%{q}%", f"%{q}%"]
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
            SELECT id, title, content, category, publish_date
            FROM policies
            WHERE {where_clause}
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    WHEN content LIKE ? THEN 2
                    ELSE 3
                END,
                publish_date DESC
            LIMIT ?
        """, params + [f"%{q}%", f"%{q}%", limit])
        
        rows = cursor.fetchall()
        
        items = [
            {
                "id": row['id'],
                "title": row['title'],
                "content": row['content'][:200] + "..." if len(row['content']) > 200 else row['content'],
                "category": row['category'],
                "publish_date": row['publish_date'],
                "source": ""
            }
            for row in rows
        ]
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": len(items),
                "query": q
            },
            "message": ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/policies/prefectures")
async def get_prefecture_policies(
    prefecture: str = Query(..., description="地州名称")
) -> Dict[str, Any]:
    """
    获取指定地州的政策
    
    - **prefecture**: 地州名称（如：文山州、昆明市等）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, title, content, category, publish_date
            FROM policies
            WHERE content LIKE ?
            ORDER BY publish_date DESC
            LIMIT 20
        """, (f"%{prefecture}%",))
        
        rows = cursor.fetchall()
        
        items = [
            {
                "id": row['id'],
                "title": row['title'],
                "content": row['content'],
                "category": row['category'],
                "publish_date": row['publish_date'],
                "source": ""
            }
            for row in rows
        ]
        
        return {
            "success": True,
            "data": {
                "items": items,
                "total": len(items),
                "prefecture": prefecture
            },
            "message": ""
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("/policies/{policy_id}")
async def get_policy_detail(policy_id: int) -> Dict[str, Any]:
    """
    获取政策详情
    
    - **policy_id**: 政策ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, title, content, category, publish_date FROM policies WHERE id = ?",
            (policy_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="政策不存在")
        
        return {
            "success": True,
            "data": {
                "id": row['id'],
                "title": row['title'],
                "content": row['content'],
                "category": row['category'],
                "publish_date": row['publish_date'],
                "source": ""
            },
            "message": ""
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
