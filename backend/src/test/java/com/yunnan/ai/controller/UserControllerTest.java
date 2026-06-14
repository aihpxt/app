package com.yunnan.ai.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(UserController.class)
@SuppressWarnings("null")
public class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testRegister() throws Exception {
        String requestBody = "{\"phone\": \"13800138000\", \"password\": \"123456\", \"nickname\": \"测试用户\"}";
        
        mockMvc.perform(post("/api/user/register")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.message").value("注册成功"));
    }

    @Test
    public void testLogin() throws Exception {
        String requestBody = "{\"phone\": \"13800138000\", \"password\": \"123456\"}";
        
        mockMvc.perform(post("/api/user/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.token").exists());
    }

    @Test
    public void testGetUserInfo() throws Exception {
        mockMvc.perform(get("/api/user/info")
                .header("Authorization", "Bearer mock_token"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.phone").value("13800138000"));
    }
}