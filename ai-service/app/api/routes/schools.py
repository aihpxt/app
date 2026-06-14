"""学校信息API路由"""
from fastapi import APIRouter, Query, Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.utils.db import query_one, query_all, execute

router = APIRouter()

class School(BaseModel):
    id: int
    name: str
    type: Optional[int] = None
    type_name: Optional[str] = None
    nature: Optional[str] = None
    min_score: Optional[float] = None
    min_rank: Optional[int] = None
    max_score: Optional[float] = None
    avg_score: Optional[float] = None
    one_rate: Optional[float] = None
    boarding: Optional[int] = None
    tuition: Optional[int] = None
    style: Optional[str] = None
    features: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    prefecture: Optional[str] = None
    level: Optional[str] = None
    logo: Optional[str] = None
    view_count: Optional[int] = None
    student_count: Optional[int] = None
    teacher_count: Optional[int] = None
    is_public: Optional[int] = None
    is_key: Optional[int] = None
    admission_history: Optional[List[Dict[str, Any]]] = None

SCHOOL_FIELDS = """
    id, name, type, type_name, 
    CASE WHEN is_public = 1 THEN '公办' WHEN is_public = 0 THEN '民办' ELSE NULL END as nature,
    min_score, min_rank, 
    one_rate, boarding, tuition, style, features, address, phone, website, 
    description, city, prefecture, level, logo, view_count, max_score, avg_score, 
    student_count, teacher_count, is_public, is_key
"""

def school_row_to_dict(row):
    """将学校数据行转换为字典"""
    data = dict(row) if row else None
    if data and data.get('logo'):
        # 清理logo URL中的反引号
        data['logo'] = data['logo'].replace('`', '')
        # 将square改为square_hd提高清晰度
        data['logo'] = data['logo'].replace('image_size=square', 'image_size=square_hd')
    return data

def build_response(success: bool, data: Any, message: str = ""):
    """构建统一响应格式"""
    return {"success": success, "data": data, "message": message}

@router.get("/schools")
async def get_school_list(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    city: Optional[str] = Query(None, description="城市筛选"),
    school_type: Optional[str] = Query(None, description="学校类型筛选"),
    level: Optional[str] = Query(None, description="学校等级筛选"),
    nature: Optional[str] = Query(None, description="学校性质筛选(公办/民办)"),
    min_score: Optional[float] = Query(None, description="最低录取分数"),
    max_score: Optional[float] = Query(None, description="最高录取分数"),
    sort_by: Optional[str] = Query("default", description="排序方式: default/score_desc/score_asc/views")
):
    """获取学校列表"""
    try:
        where_clause, params = build_where_clause(keyword, city, school_type, level, nature, min_score, max_score)
        offset = (page - 1) * size
        
        # 排序逻辑
        order_clause = "ORDER BY min_score DESC, id DESC"
        if sort_by == "score_desc":
            order_clause = "ORDER BY min_score DESC, id DESC"
        elif sort_by == "score_asc":
            order_clause = "ORDER BY min_score ASC, id DESC"
        elif sort_by == "views":
            order_clause = "ORDER BY view_count DESC, id DESC"
        
        count = query_one(f"SELECT COUNT(*) as total FROM schools WHERE {where_clause}", params)
        total = count['total'] if count else 0
        
        # 获取统计数据（所有符合条件的学校，不只是当前页）
        stats = query_one(f"""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_public = 1 THEN 1 ELSE 0 END) as public_count,
                SUM(CASE WHEN is_public = 0 THEN 1 ELSE 0 END) as private_count,
                SUM(CASE WHEN is_key = 1 THEN 1 ELSE 0 END) as key_count
            FROM schools 
            WHERE {where_clause}
        """, params)
        
        rows = query_all(f"""
            SELECT {SCHOOL_FIELDS} FROM schools 
            WHERE {where_clause} 
            {order_clause}
            LIMIT ? OFFSET ?
        """, params + [size, offset])
        
        schools = [School(**school_row_to_dict(row)) for row in rows]
        
        return build_response(True, {
            "items": schools, 
            "total": total, 
            "page": page, 
            "size": size,
            "statistics": {
                "total": stats['total'] if stats else 0,
                "public_count": stats['public_count'] if stats else 0,
                "private_count": stats['private_count'] if stats else 0,
                "key_count": stats['key_count'] if stats else 0
            }
        })
    except Exception as e:
        return build_response(False, {"items": [], "total": 0, "page": page, "size": size}, str(e))

def build_where_clause(keyword=None, city=None, school_type=None, level=None, nature=None, min_score=None, max_score=None):
    """构建WHERE子句"""
    conditions = []
    params = []
    
    if keyword:
        conditions.append("name LIKE ?")
        params.append(f"%{keyword}%")
    if city:
        conditions.append("(city = ? OR prefecture = ?)")
        params.extend([city, city])
    if school_type:
        conditions.append("typeName = ?")
        params.append(school_type)
    if level:
        conditions.append("level = ?")
        params.append(level)
    if nature:
        if nature == "公办":
            conditions.append("(is_public = 1 OR tuition = 0)")
        elif nature == "民办":
            conditions.append("(is_public = 0 OR tuition > 0)")
    if min_score is not None:
        conditions.append("minScore >= ?")
        params.append(min_score)
    if max_score is not None:
        conditions.append("minScore <= ?")
        params.append(max_score)
    
    return " AND ".join(conditions) if conditions else "1=1", params

@router.get("/schools/search")
async def search_schools(
    q: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """搜索学校"""
    return await get_school_list(keyword=q, page=page, size=size)

@router.get("/schools/cities")
async def get_cities():
    """获取所有城市列表（仅云南省）"""
    try:
        yunnan_cities = ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', 
                         '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州']
        placeholders = ','.join(['?' for _ in yunnan_cities])
        rows = query_all(f"""
            SELECT DISTINCT prefecture FROM schools 
            WHERE prefecture IN ({placeholders}) AND prefecture IS NOT NULL AND prefecture != '' 
            ORDER BY prefecture
        """, yunnan_cities)
        cities = [row['prefecture'] for row in rows]
        return build_response(True, cities)
    except Exception as e:
        return build_response(False, [], str(e))

@router.get("/schools/levels")
async def get_levels():
    """获取所有学校等级（仅云南省）"""
    try:
        yunnan_cities = ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', 
                         '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州']
        placeholders = ','.join(['?' for _ in yunnan_cities])
        rows = query_all(f"""
            SELECT DISTINCT level FROM schools 
            WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders})) AND level IS NOT NULL AND level != '' 
            ORDER BY level
        """, yunnan_cities * 2)
        levels = [row['level'] for row in rows]
        return build_response(True, levels)
    except Exception as e:
        return build_response(False, [], str(e))

@router.get("/schools/types")
async def get_school_types():
    """获取所有学校类型（仅云南省）"""
    try:
        yunnan_cities = ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', 
                         '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州']
        placeholders = ','.join(['?' for _ in yunnan_cities])
        rows = query_all(f"""
            SELECT DISTINCT typeName FROM schools 
            WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders})) AND typeName IS NOT NULL AND typeName != '' 
            ORDER BY typeName
        """, yunnan_cities * 2)
        types = [row['typeName'] for row in rows]
        return build_response(True, types)
    except Exception as e:
        return build_response(False, [], str(e))

@router.get("/schools/stats")
async def get_school_stats():
    """获取学校统计数据（仅云南省）"""
    try:
        yunnan_cities = ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', 
                         '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州']
        placeholders = ','.join(['?' for _ in yunnan_cities])
        
        where_clause = f"WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders}))"
        
        total = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause}", yunnan_cities * 2)['count']
        public_count = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (is_public = 1 OR tuition = 0)", yunnan_cities * 2)['count']
        private_count = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (is_public = 0 OR tuition > 0)", yunnan_cities * 2)['count']
        key_count = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (type = 2 OR level LIKE '%一级%')", yunnan_cities * 2)['count']
        
        # 各州市学校数量
        city_rows = query_all(f"""
            SELECT COALESCE(prefecture, city, '未知') as city_name, COUNT(*) as count 
            FROM schools 
            {where_clause}
            GROUP BY COALESCE(prefecture, city) 
            ORDER BY count DESC
        """, yunnan_cities * 2)
        city_stats = [{'name': r['city_name'], 'count': r['count']} for r in city_rows]
        
        return build_response(True, {
            'total': total,
            'public_count': public_count,
            'private_count': private_count,
            'key_count': key_count,
            'city_stats': city_stats
        })
    except Exception as e:
        return build_response(False, {}, str(e))

@router.get("/schools/{school_id}")
async def get_school_detail(school_id: int = Path(..., description="学校ID")):
    """获取学校详情"""
    try:
        row = query_one(f"SELECT {SCHOOL_FIELDS} FROM schools WHERE id = ?", [school_id])
        
        if not row:
            return build_response(False, None, "学校不存在")
        
        execute("UPDATE schools SET view_count = view_count + 1 WHERE id = ?", [school_id])
        
        school_data = school_row_to_dict(row)
        
        history_rows = query_all("""
            SELECT year, min_score, max_score, avg_score, one_rate, student_count, min_rank
            FROM school_admission_history WHERE school_id = ? ORDER BY year DESC
        """, [school_id])
        
        school_data['admission_history'] = [dict(r) for r in history_rows]
        
        return build_response(True, school_data)
    except Exception as e:
        return build_response(False, None, str(e))

@router.get("/schools/{school_id}/related")
async def get_related_schools(
    school_id: int = Path(..., description="学校ID"),
    limit: int = Query(5, ge=1, le=20, description="返回数量")
):
    """获取相关学校推荐"""
    try:
        school = query_one(f"SELECT {SCHOOL_FIELDS} FROM schools WHERE id = ?", [school_id])
        if not school:
            return build_response(False, [], "学校不存在")
        
        prefecture = school.get('prefecture') or school.get('city')
        school_type = school.get('type_name') or school.get('type')
        
        conditions = ["id != ?"]
        params = [school_id]
        
        if prefecture:
            conditions.append("(prefecture = ? OR city = ?)")
            params.extend([prefecture, prefecture])
        
        query = f"SELECT {SCHOOL_FIELDS} FROM schools WHERE {' AND '.join(conditions)} ORDER BY minScore DESC LIMIT ?"
        params.append(limit)
        
        rows = query_all(query, params)
        schools = [school_row_to_dict(row) for row in rows]
        
        return build_response(True, schools)
    except Exception as e:
        return build_response(False, [], str(e))

@router.post("/schools/batch")
async def get_schools_batch(school_ids: List[int]):
    """批量获取学校信息（用于对比功能）"""
    try:
        if not school_ids or len(school_ids) < 2:
            return build_response(False, [], "请提供至少2个学校ID")
        
        placeholders = ','.join(['?' for _ in school_ids])
        rows = query_all(f"SELECT {SCHOOL_FIELDS} FROM schools WHERE id IN ({placeholders}) ORDER BY minScore DESC", school_ids)
        schools = [school_row_to_dict(row) for row in rows]
        
        return build_response(True, schools)
    except Exception as e:
        return build_response(False, [], str(e))