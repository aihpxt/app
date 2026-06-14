"""学校信息API路由"""
from fastapi import APIRouter, Query, Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.utils.db import query_one, query_all, execute

router = APIRouter()


class School(BaseModel):
    id: int
    name: Optional[str] = None
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

YUNNAN_CITIES = ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市',
                 '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州']


def school_row_to_dict(row):
    """将学校数据行转换为字典"""
    data = dict(row) if row else None
    if data and data.get('logo'):
        data['logo'] = data['logo'].replace('`', '')
        data['logo'] = data['logo'].replace('image_size=square', 'image_size=square_hd')
    return data


def build_response(success: bool, data: Any, message: str = ""):
    """构建统一响应格式"""
    return {"success": success, "data": data, "message": message}


def _safe_get(row, key, default=None):
    """安全获取查询结果的字段，row 可能是 Row、dict 或 None"""
    if row is None:
        return default
    try:
        return row[key]
    except (KeyError, TypeError, IndexError):
        try:
            return getattr(row, key, default)
        except Exception:
            return default


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
        total = _safe_get(count, 'total', 0) or 0

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

        schools = []
        for row in rows:
            try:
                schools.append(School(**school_row_to_dict(row)))
            except Exception:
                continue

        return build_response(True, {
            "items": schools,
            "total": total,
            "page": page,
            "size": size,
            "statistics": {
                "total": _safe_get(stats, 'total', 0) or 0,
                "public_count": _safe_get(stats, 'public_count', 0) or 0,
                "private_count": _safe_get(stats, 'private_count', 0) or 0,
                "key_count": _safe_get(stats, 'key_count', 0) or 0
            }
        })
    except Exception as e:
        return build_response(False, {"items": [], "total": 0, "page": page, "size": size}, str(e))


def build_where_clause(keyword=None, city=None, school_type=None, level=None, nature=None, min_score=None, max_score=None):
    """构建WHERE子句 - 使用下划线分隔的字段名匹配表结构"""
    conditions = []
    params = []

    if keyword:
        conditions.append("name LIKE ?")
        params.append(f"%{keyword}%")
    if city:
        conditions.append("(city = ? OR prefecture = ?)")
        params.extend([city, city])
    if school_type:
        conditions.append("(type_name = ? OR type_name = ?)")
        params.extend([school_type, school_type])
    if level:
        conditions.append("level = ?")
        params.append(level)
    if nature:
        if nature == "公办":
            conditions.append("(is_public = 1 OR tuition = 0)")
        elif nature == "民办":
            conditions.append("(is_public = 0 OR tuition > 0)")
    if min_score is not None:
        conditions.append("min_score >= ?")
        params.append(min_score)
    if max_score is not None:
        conditions.append("min_score <= ?")
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
        placeholders = ','.join(['?' for _ in YUNNAN_CITIES])
        rows = query_all(f"""
            SELECT DISTINCT prefecture FROM schools
            WHERE prefecture IN ({placeholders}) AND prefecture IS NOT NULL AND prefecture != ''
            ORDER BY prefecture
        """, YUNNAN_CITIES)
        cities = [_safe_get(r, 'prefecture') for r in rows if _safe_get(r, 'prefecture')]
        # 数据库中没有数据时，返回默认的云南城市列表
        if not cities:
            cities = list(YUNNAN_CITIES)
        return build_response(True, cities)
    except Exception as e:
        return build_response(False, list(YUNNAN_CITIES), str(e))


@router.get("/schools/levels")
async def get_levels():
    """获取所有学校等级"""
    try:
        placeholders = ','.join(['?' for _ in YUNNAN_CITIES])
        rows = query_all(f"""
            SELECT DISTINCT level FROM schools
            WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders})) AND level IS NOT NULL AND level != ''
            ORDER BY level
        """, YUNNAN_CITIES * 2)
        levels = [_safe_get(r, 'level') for r in rows if _safe_get(r, 'level')]
        if not levels:
            levels = ['一级一等', '一级二等', '一级三等', '二级一等', '二级二等', '二级三等']
        return build_response(True, levels)
    except Exception as e:
        return build_response(False, ['一级一等', '一级二等', '一级三等', '二级一等', '二级二等', '二级三等'], str(e))


@router.get("/schools/types")
async def get_school_types():
    """获取所有学校类型"""
    try:
        placeholders = ','.join(['?' for _ in YUNNAN_CITIES])
        rows = query_all(f"""
            SELECT DISTINCT type_name FROM schools
            WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders})) AND type_name IS NOT NULL AND type_name != ''
            ORDER BY type_name
        """, YUNNAN_CITIES * 2)
        types = [_safe_get(r, 'type_name') for r in rows if _safe_get(r, 'type_name')]
        if not types:
            types = ['高中', '初中', '完中']
        return build_response(True, types)
    except Exception as e:
        return build_response(False, ['高中', '初中', '完中'], str(e))


@router.get("/schools/stats")
async def get_school_stats():
    """获取学校统计数据"""
    try:
        placeholders = ','.join(['?' for _ in YUNNAN_CITIES])
        where_clause = f"WHERE (city IN ({placeholders}) OR prefecture IN ({placeholders}))"

        total_row = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause}", YUNNAN_CITIES * 2)
        public_row = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (is_public = 1 OR tuition = 0)", YUNNAN_CITIES * 2)
        private_row = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (is_public = 0 OR tuition > 0)", YUNNAN_CITIES * 2)
        key_row = query_one(f"SELECT COUNT(*) as count FROM schools {where_clause} AND (type = 2 OR level LIKE '%一级%')", YUNNAN_CITIES * 2)

        city_rows = query_all(f"""
            SELECT COALESCE(prefecture, city, '未知') as city_name, COUNT(*) as count
            FROM schools
            {where_clause}
            GROUP BY COALESCE(prefecture, city)
            ORDER BY count DESC
        """, YUNNAN_CITIES * 2)

        total = _safe_get(total_row, 'count', 0) or 0
        public_count = _safe_get(public_row, 'count', 0) or 0
        private_count = _safe_get(private_row, 'count', 0) or 0
        key_count = _safe_get(key_row, 'count', 0) or 0

        city_stats = []
        for r in city_rows:
            name = _safe_get(r, 'city_name', '未知')
            cnt = _safe_get(r, 'count', 0) or 0
            if name:
                city_stats.append({'name': name, 'count': cnt})

        return build_response(True, {
            'total': total,
            'public_count': public_count,
            'private_count': private_count,
            'key_count': key_count,
            'city_stats': city_stats
        })
    except Exception as e:
        return build_response(False, {
            'total': 0,
            'public_count': 0,
            'private_count': 0,
            'key_count': 0,
            'city_stats': []
        }, str(e))


@router.get("/schools/{school_id}")
async def get_school_detail(school_id: int = Path(..., description="学校ID")):
    """获取学校详情"""
    try:
        row = query_one(f"SELECT {SCHOOL_FIELDS} FROM schools WHERE id = ?", [school_id])

        if not row:
            return build_response(False, None, "学校不存在")

        try:
            execute("UPDATE schools SET view_count = view_count + 1 WHERE id = ?", [school_id])
        except Exception:
            pass

        school_data = school_row_to_dict(row)

        history_rows = query_all("""
            SELECT year, min_score, max_score, avg_score, one_rate, student_count, min_rank
            FROM school_admission_history WHERE school_id = ? ORDER BY year DESC
        """, [school_id])

        if history_rows:
            school_data['admission_history'] = [dict(r) for r in history_rows]
        else:
            school_data['admission_history'] = []

        return build_response(True, school_data)
    except Exception as e:
        return build_response(False, None, str(e))


@router.get("/schools/compare")
async def compare_schools():
    """比较学校（占位接口）"""
    return build_response(True, [], "compare schools placeholder")


@router.post("/schools/favorite")
async def favorite_school():
    """收藏学校（占位接口）"""
    return build_response(True, {}, "favorite placeholder")


@router.delete("/schools/favorite/{school_id}")
async def unfavorite_school(school_id: int = Path(...)):
    """取消收藏（占位接口）"""
    return build_response(True, {}, "unfavorite placeholder")


@router.get("/schools/favorites")
async def get_favorites():
    """获取收藏列表（占位接口）"""
    return build_response(True, [], "favorites placeholder")
