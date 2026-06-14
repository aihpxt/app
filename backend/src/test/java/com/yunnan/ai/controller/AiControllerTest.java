package com.yunnan.ai.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AiController.class)
@SuppressWarnings("null")
public class AiControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void testPredictAdmissionProbability() throws Exception {
        String requestBody = "{\"totalScore\": 650, \"rank\": 2000, \"city\": \"昆明市\", \"targetSchoolId\": 1}";
        
        mockMvc.perform(post("/api/ai/predict")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.admissionProbability").exists());
    }

    @Test
    public void testRecommendSchools() throws Exception {
        String requestBody = "{\"studentData\": {\"totalScore\": 650, \"rank\": 2000, \"city\": \"昆明市\"}}";
        
        mockMvc.perform(post("/api/ai/recommend")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.recommendations").isArray());
    }

    @Test
    public void testHealthCheck() throws Exception {
        mockMvc.perform(get("/api/ai/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.status").value("healthy"));
    }
}