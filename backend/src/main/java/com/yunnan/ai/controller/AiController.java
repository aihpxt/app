package com.yunnan.ai.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import java.util.*;

@RestController
@RequestMapping("/ai")
@CrossOrigin(origins = "*")
public class AiController {



    @PostMapping("/predict")
    public ResponseEntity<Map<String, Object>> predictAdmissionProbability(@RequestBody Map<String, Object> studentData) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            // 调用AI服务进行预测
            // 这里模拟AI服务的调用
            double totalScore = ((Number) studentData.get("totalScore")).doubleValue();
            int rank = ((Number) studentData.get("rank")).intValue();
            
            // 模拟预测算法
            double probability = calculateProbability(totalScore, rank);
            
            Map<String, Object> data = new HashMap<>();
            data.put("admissionProbability", Math.round(probability * 100.0) / 100.0);
            data.put("confidence", 92.5);
            data.put("analysis", "基于历史数据和AI模型分析，您的分数和排名在目标学校的录取范围内");
            
            response.put("success", true);
            response.put("message", "预测成功");
            response.put("data", data);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "预测失败: " + e.getMessage());
            response.put("data", null);
        }
        
        return ResponseEntity.ok(response);
    }

    @PostMapping("/recommend")
    public ResponseEntity<Map<String, Object>> recommendSchools(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            
            List<Map<String, Object>> recommendations = new ArrayList<>();
            
            // 模拟推荐算法
            Map<String, Object> rec1 = new HashMap<>();
            rec1.put("schoolId", 1);
            rec1.put("schoolName", "云南省第一中学");
            rec1.put("matchScore", 95.0);
            rec1.put("admissionProbability", 88.0);
            rec1.put("reason", "分数和排名均达到录取要求，匹配度极高");
            recommendations.add(rec1);
            
            Map<String, Object> rec2 = new HashMap<>();
            rec2.put("schoolId", 2);
            rec2.put("schoolName", "昆明市第二中学");
            rec2.put("matchScore", 88.0);
            rec2.put("admissionProbability", 92.0);
            rec2.put("reason", "分数超过录取线，录取概率较高");
            recommendations.add(rec2);
            
            Map<String, Object> rec3 = new HashMap<>();
            rec3.put("schoolId", 3);
            rec3.put("schoolName", "昆明市第三中学");
            rec3.put("matchScore", 82.0);
            rec3.put("admissionProbability", 85.0);
            rec3.put("reason", "排名在录取范围内，建议作为稳妥选择");
            recommendations.add(rec3);
            
            Map<String, Object> rec4 = new HashMap<>();
            rec4.put("schoolId", 4);
            rec4.put("schoolName", "昆明市第十中学");
            rec4.put("matchScore", 78.0);
            rec4.put("admissionProbability", 80.0);
            rec4.put("reason", "分数接近录取线，可作为保底选择");
            recommendations.add(rec4);
            
            Map<String, Object> data = new HashMap<>();
            data.put("recommendations", recommendations);
            data.put("totalCount", recommendations.size());
            data.put("analysisSummary", "根据您的分数和排名，为您推荐4所匹配度较高的学校");
            
            response.put("success", true);
            response.put("message", "推荐成功");
            response.put("data", data);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "推荐失败: " + e.getMessage());
            response.put("data", null);
        }
        
        return ResponseEntity.ok(response);
    }

    @PostMapping("/interpret")
    public ResponseEntity<Map<String, Object>> interpretPolicy(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            
            Map<String, Object> interpretation = new HashMap<>();
            
            List<String> keyPoints = new ArrayList<>();
            keyPoints.add("统一考试时间为6月16-18日");
            keyPoints.add("总分750分，包含多个科目");
            keyPoints.add("按照\"分数优先、遵循志愿\"原则录取");
            keyPoints.add("招生录取工作将分批次进行");
            
            interpretation.put("keyPoints", keyPoints);
            interpretation.put("impact", "该政策对全省考生都有重要影响，考生需要合理安排复习时间，注意各科均衡发展。录取原则强调分数优先，因此提高总分是关键。");
            interpretation.put("suggestions", "建议考生：1）制定科学的复习计划；2）关注各科均衡发展；3）了解志愿填报规则；4）及时关注政策变化。");
            interpretation.put("confidence", 95.0);
            
            response.put("success", true);
            response.put("message", "解读成功");
            response.put("data", interpretation);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "解读失败: " + e.getMessage());
            response.put("data", null);
        }
        
        return ResponseEntity.ok(response);
    }

    @PostMapping("/calibrate")
    public ResponseEntity<Map<String, Object>> calibrateScore(@RequestBody Map<String, Object> request) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            double originalScore = ((Number) request.get("originalScore")).doubleValue();
            
            // 模拟分数校准算法
            double calibratedScore = originalScore * 1.02; // 模拟校准
            int estimatedRank = (int) (100000 - calibratedScore * 100);
            
            Map<String, Object> data = new HashMap<>();
            data.put("originalScore", originalScore);
            data.put("calibratedScore", Math.round(calibratedScore * 100.0) / 100.0);
            data.put("estimatedRank", estimatedRank);
            data.put("calibrationFactor", 1.02);
            data.put("confidence", 88.5);
            
            response.put("success", true);
            response.put("message", "校准成功");
            response.put("data", data);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "校准失败: " + e.getMessage());
            response.put("data", null);
        }
        
        return ResponseEntity.ok(response);
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "AI服务运行正常");
        response.put("data", Map.of("status", "healthy", "version", "1.0.0"));
        return ResponseEntity.ok(response);
    }

    private double calculateProbability(double totalScore, int rank) {
        // 简化的预测算法
        double baseProb = 0.7;
        double scoreFactor = totalScore / 750.0 * 0.2;
        double rankFactor = Math.max(0, 1.0 - rank / 10000.0) * 0.1;
        
        return Math.min(0.99, baseProb + scoreFactor + rankFactor);
    }
}