package com.aiphxt.client;

import com.aiphxt.config.FeignConfig;
import com.aiphxt.dto.*;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.Map;

@FeignClient(name = "ai-service", url = "${ai.service.url}", configuration = FeignConfig.class)
public interface AiServiceClient {

    @PostMapping("/api/v1/ai/recommend")
    Map<String, Object> recommendSchools(@RequestBody SchoolRecommendationRequest request);

    @PostMapping("/api/v1/ai/predict")
    Map<String, Object> predictAdmission(@RequestBody AdmissionPredictionRequest request);

    @PostMapping("/api/v1/ai/generate-plan")
    Map<String, Object> generateVolunteerPlan(@RequestBody VolunteerPlanRequest request);

    @PostMapping("/api/v1/ai/interpret-policy")
    Map<String, Object> interpretPolicy(@RequestBody PolicyInterpretationRequest request);

}