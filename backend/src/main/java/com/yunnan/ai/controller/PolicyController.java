package com.yunnan.ai.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/policies")
@CrossOrigin(origins = "*")
public class PolicyController {

    @GetMapping("")
    public ResponseEntity<Map<String, Object>> getPolicyList(
            @RequestParam(required = false) Integer page,
            @RequestParam(required = false) Integer pageSize,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String keyword) {
        
        Map<String, Object> response = new HashMap<>();
        List<Map<String, Object>> policies = new ArrayList<>();
        
        // 模拟政策数据
        Map<String, Object> policy1 = new HashMap<>();
        policy1.put("id", 1);
        policy1.put("title", "2026年昆明市中考招生政策解读");
        policy1.put("type", "招生政策");
        policy1.put("publishDate", "2026-03-15");
        policy1.put("summary", "2026年昆明市中考招生政策主要包括：报名时间、考试科目、录取规则等内容。");
        policy1.put("content", "2026年昆明市中考招生政策要点：\n1. 报名时间：2026年3月20日-4月10日\n2. 考试科目：语文、数学、英语、物理、化学、道德与法治、历史、体育\n3. 录取规则：按分数从高到低录取，遵循志愿填报顺序\n4. 特长生招生：体育、艺术特长生可提前批次录取");
        
        Map<String, Object> policy2 = new HashMap<>();
        policy2.put("id", 2);
        policy2.put("title", "云南省普通高中招生改革方案");
        policy2.put("type", "改革方案");
        policy2.put("publishDate", "2026-02-20");
        policy2.put("summary", "云南省普通高中招生改革方案正式发布，全面推进素质教育。");
        policy2.put("content", "云南省普通高中招生改革方案要点：\n1. 推进综合素质评价纳入录取参考\n2. 扩大普通高中招生自主权\n3. 优化志愿填报方式，实行平行志愿\n4. 加强中考命题改革，注重能力考查");
        
        Map<String, Object> policy3 = new HashMap<>();
        policy3.put("id", 3);
        policy3.put("title", "昆明市优质高中指标到校政策说明");
        policy3.put("type", "指标到校");
        policy3.put("publishDate", "2026-01-10");
        policy3.put("summary", "昆明市优质高中指标到校政策详解，让更多学生有机会进入优质高中。");
        policy3.put("content", "昆明市优质高中指标到校政策：\n1. 指标到校比例：优质高中招生计划的50%分配到各初中学校\n2. 分配原则：根据初中学校毕业生人数、办学质量等因素综合分配\n3. 录取要求：指标到校生需达到本校录取分数线下降一定分数\n4. 实施目的：促进教育公平，均衡教育资源配置");
        
        policies.add(policy1);
        policies.add(policy2);
        policies.add(policy3);
        
        response.put("success", true);
        response.put("message", "获取成功");
        response.put("data", policies);
        response.put("total", 3);
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getPolicyDetail(@PathVariable Long id) {
        Map<String, Object> response = new HashMap<>();
        
        // 模拟政策详情数据
        Map<String, Object> policy = new HashMap<>();
        policy.put("id", id);
        policy.put("title", "2026年昆明市中考招生政策解读");
        policy.put("type", "招生政策");
        policy.put("publishDate", "2026-03-15");
        policy.put("summary", "2026年昆明市中考招生政策主要包括：报名时间、考试科目、录取规则等内容。");
        policy.put("content", "2026年昆明市中考招生政策要点：\n1. 报名时间：2026年3月20日-4月10日\n2. 考试科目：语文、数学、英语、物理、化学、道德与法治、历史、体育\n3. 录取规则：按分数从高到低录取，遵循志愿填报顺序\n4. 特长生招生：体育、艺术特长生可提前批次录取");
        
        response.put("success", true);
        response.put("message", "获取成功");
        response.put("data", policy);
        
        return ResponseEntity.ok(response);
    }
}
