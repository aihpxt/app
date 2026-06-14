package com.aiphxt.service;

import com.aiphxt.client.AiServiceClient;
import com.aiphxt.dto.*;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class AiService {

    private final AiServiceClient aiServiceClient;

    public AiService(AiServiceClient aiServiceClient) {
        this.aiServiceClient = aiServiceClient;
    }

    public Map<String, Object> recommendSchools(SchoolRecommendationRequest request) {
        return aiServiceClient.recommendSchools(request);
    }

    public Map<String, Object> predictAdmission(AdmissionPredictionRequest request) {
        return aiServiceClient.predictAdmission(request);
    }

    public Map<String, Object> generateVolunteerPlan(VolunteerPlanRequest request) {
        return aiServiceClient.generateVolunteerPlan(request);
    }

    public Map<String, Object> interpretPolicy(PolicyInterpretationRequest request) {
        return aiServiceClient.interpretPolicy(request);
    }

}