package com.yunnan.ai.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/test")
@CrossOrigin(origins = "*")
public class TestController {

    @GetMapping("/ping")
    public ResponseEntity<Map<String, Object>> ping() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "pong");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@RequestBody Map<String, String> request) {
        Map<String, Object> response = new HashMap<>();
        Map<String, Object> data = new HashMap<>();
        data.put("token", "mock_token_123456");
        data.put("userId", 1);
        data.put("phone", request.get("phone"));
        data.put("role", 1);
        
        response.put("success", true);
        response.put("message", "登录成功");
        response.put("data", data);
        return ResponseEntity.ok(response);
    }
}
