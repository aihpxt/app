#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文章信息API路由"""

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


@router.get("/articles")
async def get_articles(
    category: Optional[str] = Query(None, description="文章分类"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
) -> Dict[str, Any]:
    """
    获取文章列表
    
    - **category**: 文章分类（招生录取、政策解读等）
    - **keyword**: 关键词搜索
    - **page**: 页码
    - **size**: 每页数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        conditions = []
        params = []
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if keyword:
            conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        count_sql = f"SELECT COUNT(*) as total FROM articles WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        offset = (page - 1) * size
        query_sql = f"""
            SELECT id, title, url, summary, pub_time, source, category
            FROM articles
            WHERE {where_clause}
            ORDER BY pub_time DESC, id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        
        cursor.execute(query_sql, params)
        rows = cursor.fetchall()
        
        items = [
            {
                "id": row['id'],
                "title": row['title'],
                "url": row['url'],
                "summary": row['summary'] if row['summary'] else "",
                "pub_time": row['pub_time'] if row['pub_time'] else "",
                "source": row['source'] if row['source'] else "",
                "category": row['category'] if row['category'] else ""
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


@router.get("/articles/categories")
async def get_categories() -> Dict[str, Any]:
    """获取所有文章分类"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM articles 
            WHERE category IS NOT NULL AND category != ''
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


@router.get("/articles/search")
async def search_articles(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="文章分类"),
    limit: int = Query(10, ge=1, le=50, description="返回数量")
) -> Dict[str, Any]:
    """
    搜索文章
    
    - **q**: 搜索关键词
    - **category**: 文章分类
    - **limit**: 返回数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        conditions = ["(title LIKE ? OR content LIKE ? OR summary LIKE ?)"]
        params = [f"%{q}%", f"%{q}%", f"%{q}%"]
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions)
        
        cursor.execute(f"""
            SELECT id, title, url, summary, pub_time, source, category
            FROM articles
            WHERE {where_clause}
            ORDER BY pub_time DESC
            LIMIT ?
        """, params + [limit])
        
        rows = cursor.fetchall()
        
        items = [
            {
                "id": row['id'],
                "title": row['title'],
                "url": row['url'],
                "summary": row['summary'][:150] + "..." if row['summary'] and len(row['summary']) > 150 else (row['summary'] if row['summary'] else ""),
                "pub_time": row['pub_time'] if row['pub_time'] else "",
                "source": row['source'] if row['source'] else "",
                "category": row['category'] if row['category'] else ""
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


@router.get("/articles/{article_id}")
async def get_article_detail(article_id: int) -> Dict[str, Any]:
    """
    获取文章详情
    
    - **article_id**: 文章ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, title, url, content, summary, pub_time, source, category FROM articles WHERE id = ?",
            (article_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文章不存在")
        
        return {
            "success": True,
            "data": {
                "id": row['id'],
                "title": row['title'],
                "url": row['url'],
                "content": row['content'] if row['content'] else "",
                "summary": row['summary'] if row['summary'] else "",
                "pub_time": row['pub_time'] if row['pub_time'] else "",
                "source": row['source'] if row['source'] else "",
                "category": row['category'] if row['category'] else ""
            },
            "message": ""
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()