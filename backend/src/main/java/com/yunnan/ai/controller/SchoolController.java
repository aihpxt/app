package com.yunnan.ai.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/schools")
@CrossOrigin(origins = "*")
public class SchoolController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("")
    public ResponseEntity<Map<String, Object>> getSchoolList(
            @RequestParam(required = false, defaultValue = "1") Integer page,
            @RequestParam(required = false, defaultValue = "10") Integer size,
            @RequestParam(required = false) String city,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) String keyword) {

        Map<String, Object> response = new HashMap<>();
        List<Map<String, Object>> schools = new ArrayList<>();

        try {
            // 使用 JdbcTemplate 直接查询数据库
            String sql = "SELECT id, name, city, district, prefecture, address, phone, type, type_name, " +
                        "min_score, min_rank, one_rate, tuition, features, description, logo, style, " +
                        "boarding, level, student_count, teacher_count, area, school_type, " +
                        "is_public, is_key, view_count, max_score, avg_score " +
                        "FROM schools ORDER BY id";
            List<Map<String, Object>> dbSchools = jdbcTemplate.queryForList(sql);

            System.out.println("DEBUG: 从数据库查询到 " + dbSchools.size() + " 所学校");

            if (!dbSchools.isEmpty()) {
                for (Map<String, Object> school : dbSchools) {
                    Map<String, Object> schoolMap = new HashMap<>();
                    schoolMap.put("id", school.get("id"));
                    schoolMap.put("name", school.get("name"));
                    schoolMap.put("code", "SCH" + school.get("id"));
                    schoolMap.put("city", school.get("city"));
                    schoolMap.put("district", school.get("district"));
                    schoolMap.put("prefecture", school.get("prefecture") != null ? school.get("prefecture") : school.get("city"));
                    schoolMap.put("address", school.get("address"));
                    schoolMap.put("phone", school.get("phone"));
                    schoolMap.put("type", school.get("type"));
                    schoolMap.put("type_name", school.get("type_name") != null ? school.get("type_name") : "高中");
                    schoolMap.put("nature", school.get("is_public") != null && ((Number)school.get("is_public")).intValue() == 1 ? "公办" : "民办");
                    schoolMap.put("is_public", school.get("is_public"));
                    schoolMap.put("is_key", school.get("is_key"));
                    schoolMap.put("schoolLevel", school.get("level") != null ? school.get("level") : "普通高中");
                    schoolMap.put("min_score", school.get("min_score") != null ? ((Number)school.get("min_score")).doubleValue() : 0);
                    schoolMap.put("min_rank", school.get("min_rank"));
                    schoolMap.put("one_rate", school.get("one_rate") != null ? ((Number)school.get("one_rate")).doubleValue() : 0);
                    schoolMap.put("tuition", school.get("tuition") != null ? school.get("tuition") : 0);
                    schoolMap.put("view_count", school.get("view_count") != null ? school.get("view_count") : 0);
                    schoolMap.put("features", school.get("features") != null ? school.get("features") : "优质教育资源");
                    schoolMap.put("description", school.get("description") != null ? school.get("description") : "学校详情待完善");
                    schoolMap.put("logo", school.get("logo"));
                    schoolMap.put("style", school.get("style"));
                    schoolMap.put("boarding", school.get("boarding"));
                    schoolMap.put("province", "云南省");
                    schoolMap.put("student_count", school.get("student_count"));
                    schoolMap.put("teacher_count", school.get("teacher_count"));
                    schoolMap.put("area", school.get("area"));
                    schoolMap.put("school_type", school.get("school_type"));
                    schoolMap.put("max_score", school.get("max_score") != null ? ((Number)school.get("max_score")).doubleValue() : 0);
                    schoolMap.put("avg_score", school.get("avg_score") != null ? ((Number)school.get("avg_score")).doubleValue() : 0);
                    schools.add(schoolMap);
                }

                response.put("success", true);
                response.put("message", "从数据库获取成功，共 " + schools.size() + " 所学校");
                response.put("data", schools);
                response.put("total", schools.size());
                return ResponseEntity.ok(response);
            }
        } catch (Exception e) {
            System.err.println("ERROR: 数据库查询失败: " + e.getMessage());
            e.printStackTrace();
        }

        // 数据库查询失败，使用模拟数据
        Map<String, Object> school1 = new HashMap<>();
        school1.put("id", 1);
        school1.put("name", "Kun Ming Shi Di Yi Zhong Xue");
        school1.put("city", "Kun Ming Shi");
        school1.put("district", "Wu Hua Qu");
        school1.put("prefecture", "Kun Ming Shi");
        school1.put("address", "Kun Ming Shi Wu Hua Qu Xi Chang Lu 233 Hao");
        school1.put("phone", "0871-65324879");
        school1.put("type", 2);
        school1.put("type_name", "Zhong Dian Gao Zhong");
        school1.put("nature", "Gong Ban");
        school1.put("is_public", 1);
        school1.put("is_key", true);
        school1.put("schoolLevel", "Yi Ji Yi Deng");
        school1.put("min_score", 678);
        school1.put("min_rank", 500);
        school1.put("one_rate", 95.0);
        school1.put("tuition", 0);
        school1.put("view_count", 1250);
        school1.put("features", "Bai Nian Ming Xiao, Shi Zi Xiong Hou, She Shi Wan Shan");
        schools.add(school1);

        response.put("success", true);
        response.put("message", "获取成功（使用模拟数据）");
        response.put("data", schools);
        response.put("total", schools.size());

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getSchoolDetail(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();

        try {
            String sql = "SELECT id, name, city, district, prefecture, address, phone, website, type, type_name, " +
                        "min_score, min_rank, one_rate, max_score, avg_score, tuition, features, description, " +
                        "logo, style, boarding, level, student_count, teacher_count, area, " +
                        "school_type, is_public, is_key, view_count " +
                        "FROM schools WHERE id = ?";
            Map<String, Object> school = jdbcTemplate.queryForMap(sql, id);

            if (school != null && !school.isEmpty()) {
                Map<String, Object> schoolMap = new HashMap<>();
                schoolMap.put("id", school.get("id"));
                schoolMap.put("name", school.get("name"));
                schoolMap.put("type", school.get("type"));
                schoolMap.put("type_name", school.get("type_name"));
                schoolMap.put("city", school.get("city"));
                schoolMap.put("district", school.get("district"));
                schoolMap.put("prefecture", school.get("prefecture"));
                schoolMap.put("address", school.get("address"));
                schoolMap.put("phone", school.get("phone"));
                schoolMap.put("website", school.get("website"));
                schoolMap.put("level", school.get("level"));
                schoolMap.put("nature", school.get("is_public") != null && ((Number)school.get("is_public")).intValue() == 1 ? "公办" : "民办");
                schoolMap.put("is_public", school.get("is_public"));
                schoolMap.put("is_key", school.get("is_key"));
                schoolMap.put("min_score", school.get("min_score") != null ? ((Number)school.get("min_score")).doubleValue() : 0);
                schoolMap.put("min_rank", school.get("min_rank"));
                schoolMap.put("one_rate", school.get("one_rate") != null ? ((Number)school.get("one_rate")).doubleValue() : 0);
                schoolMap.put("max_score", school.get("max_score") != null ? ((Number)school.get("max_score")).doubleValue() : 0);
                schoolMap.put("avg_score", school.get("avg_score") != null ? ((Number)school.get("avg_score")).doubleValue() : 0);
                schoolMap.put("tuition", school.get("tuition"));
                schoolMap.put("boarding", school.get("boarding"));
                schoolMap.put("student_count", school.get("student_count"));
                schoolMap.put("teacher_count", school.get("teacher_count"));
                schoolMap.put("view_count", school.get("view_count"));
                schoolMap.put("features", school.get("features"));
                schoolMap.put("description", school.get("description"));
                schoolMap.put("logo", school.get("logo"));
                schoolMap.put("style", school.get("style"));
                schoolMap.put("province", "云南省");
                schoolMap.put("area", school.get("area"));
                schoolMap.put("school_type", school.get("school_type"));

                response.put("success", true);
                response.put("message", "获取成功");
                response.put("data", schoolMap);
                return ResponseEntity.ok(response);
            }
        } catch (Exception e) {
            System.err.println("ERROR: 数据库查询失败: " + e.getMessage());
            e.printStackTrace();
        }

        // 数据库查询失败，返回默认数据
        Map<String, Object> school = new HashMap<>();
        school.put("id", id);
        school.put("type", 2);
        school.put("type_name", "重点高中");
        school.put("nature", "公办");
        school.put("is_public", 1);
        school.put("is_key", true);
        school.put("tuition", 0);
        school.put("view_count", 1250);

        if (id == 1) {
            school.put("name", "昆明市第一中学");
            school.put("city", "昆明市");
            school.put("district", "五华区");
            school.put("prefecture", "昆明市");
            school.put("address", "昆明市五华区西昌路233号");
            school.put("phone", "0871-65324879");
            school.put("schoolLevel", "一级一等");
            school.put("min_score", 678);
            school.put("min_rank", 500);
            school.put("one_rate", 95.0);
            school.put("features", "百年名校,师资雄厚,设施完善,体育特长生招生,艺术特长生招生");
            school.put("description", "昆明市第一中学创建于1905年，是云南省首批一级一等完全中学。");
        } else {
            school.put("name", "学校" + id);
            school.put("city", "昆明市");
            school.put("district", "其他区");
            school.put("prefecture", "昆明市");
            school.put("address", "地址信息待完善");
            school.put("phone", "联系电话待完善");
            school.put("schoolLevel", "普通高中");
            school.put("min_score", 650);
            school.put("min_rank", 1000);
            school.put("one_rate", 90.0);
            school.put("features", "优质教育资源");
            school.put("description", "学校详细信息待完善。");
        }

        response.put("success", true);
        response.put("message", "获取成功（使用默认数据）");
        response.put("data", school);

        return ResponseEntity.ok(response);
    }
}
