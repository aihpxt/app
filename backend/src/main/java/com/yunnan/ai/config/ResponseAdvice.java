package com.yunnan.ai.config;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.lang.NonNull;
import org.springframework.lang.Nullable;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class ResponseAdvice implements ResponseBodyAdvice<Object> {

    @Override
    public boolean supports(@NonNull MethodParameter returnType, @NonNull Class<? extends HttpMessageConverter<?>> converterType) {
        return true;
    }

    @Override
    public Object beforeBodyWrite(@Nullable Object body, @NonNull MethodParameter returnType, @NonNull MediaType selectedContentType,
                                  @NonNull Class<? extends HttpMessageConverter<?>> selectedConverterType,
                                  @NonNull ServerHttpRequest request, @NonNull ServerHttpResponse response) {
        // 如果已经是统一响应格式，则直接返回
        if (body instanceof Map && ((Map<?, ?>) body).containsKey("success")) {
            return body;
        }

        // 如果是String类型，需要特殊处理
        if (body instanceof String) {
            ObjectMapper objectMapper = new ObjectMapper();
            try {
                Map<String, Object> result = new HashMap<>();
                result.put("success", true);
                result.put("data", body);
                result.put("message", "操作成功");
                return objectMapper.writeValueAsString(result);
            } catch (JsonProcessingException e) {
                throw new RuntimeException(e);
            }
        }

        // 统一包装响应
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("data", body);
        result.put("message", "操作成功");
        return result;
    }
}
