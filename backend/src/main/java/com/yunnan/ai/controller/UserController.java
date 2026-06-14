package com.yunnan.ai.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/user")
@CrossOrigin(origins = "*")
public class UserController {

    @PostMapping("/register")
    public ResponseEntity<Map<String, Object>> register(@RequestBody Map<String, String> request) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "注册成功");
        response.put("data", null);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> request) {
        Map<String, Object> response = new HashMap<>();
        Map<String, Object> data = new HashMap<>();
        data.put("token", "mock_token_123456");
        data.put("userId", 1);
        String phone = request.get("phone") != null ? request.get("phone") : request.get("username");
        data.put("phone", phone);
        data.put("role", 1);
        Map<String, Object> userInfo = new HashMap<>();
        userInfo.put("id", 1);
        userInfo.put("phone", phone);
        userInfo.put("nickname", "测试用户");
        userInfo.put("role", 1);
        data.put("userInfo", userInfo);
        
        response.put("success", true);
        response.put("message", "登录成功");
        response.put("data", data);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> getUserInfo(@RequestHeader("Authorization") String token) {
        Map<String, Object> response = new HashMap<>();
        Map<String, Object> data = new HashMap<>();
        data.put("id", 1);
        data.put("phone", "13800138000");
        data.put("nickname", "测试用户");
        data.put("role", 1);
        data.put("avatar", "");
        
        response.put("success", true);
        response.put("message", "获取成功");
        response.put("data", data);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/info")
    public ResponseEntity<Map<String, Object>> updateUserInfo(@RequestHeader("Authorization") String token, 
                                                               @RequestBody Map<String, Object> userInfo) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "更新成功");
        response.put("data", userInfo);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/student/verify")
    public ResponseEntity<Map<String, Object>> verifyStudent(@RequestHeader("Authorization") String token,
                                                              @RequestBody Map<String, String> studentInfo) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "学籍核验成功");
        response.put("data", studentInfo);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/student/info")
    public ResponseEntity<Map<String, Object>> getStudentInfo(@RequestHeader("Authorization") String token) {
        Map<String, Object> response = new HashMap<>();
        Map<String, Object> data = new HashMap<>();
        data.put("id", 1);
        data.put("userId", 1);
        data.put("name", "张三");
        data.put("idCard", "530102201001011234");
        data.put("examId", "2026010001");
        data.put("city", "昆明市");
        data.put("district", "五华区");
        data.put("school", "昆明市第五中学");
        data.put("totalScore", 650.0);
        data.put("rank", 2000);
        
        response.put("success", true);
        response.put("message", "获取成功");
        response.put("data", data);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/student/info")
    public ResponseEntity<Map<String, Object>> saveStudentInfo(@RequestHeader("Authorization") String token,
                                                                @RequestBody Map<String, Object> studentInfo) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "保存成功");
        response.put("data", studentInfo);
        return ResponseEntity.ok(response);
    }
}