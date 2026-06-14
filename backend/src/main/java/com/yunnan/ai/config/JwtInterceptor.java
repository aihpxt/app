package com.yunnan.ai.config;

import com.yunnan.ai.util.JwtUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class JwtInterceptor implements HandlerInterceptor {

    @Autowired
    private JwtUtil jwtUtil;
    
    // 白名单路径，不需要token验证
    private static final String[] WHITE_LIST = {
        "/api/user/login",
        "/api/user/register",
        "/api/schools",
        "/api/policies",
        "/api/policies/",
        "/api/ai/",
        "/api/test/"
    };

    @Override
    public boolean preHandle(@NonNull HttpServletRequest request, @NonNull HttpServletResponse response, @NonNull Object handler) throws Exception {
        String requestURI = request.getRequestURI();
        
        // 处理OPTIONS请求
        if (request.getMethod().equals("OPTIONS")) {
            response.setStatus(HttpServletResponse.SC_OK);
            return true;
        }
        
        // 检查是否在白名单中
        for (String path : WHITE_LIST) {
            if (requestURI.startsWith(path)) {
                return true;
            }
        }
        
        // 从请求头获取token
        String token = request.getHeader("Authorization");
        
        // 检查token
        if (token == null || !token.startsWith("Bearer ")) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write("{\"success\": false, \"message\": \"缺少或无效的token\"}");
            return false;
        }
        
        // 提取token
        token = token.substring(7);
        
        try {
            // 验证token
            jwtUtil.validateToken(token);
            // 可以将用户信息存储到request中，供后续使用
            Long userId = jwtUtil.getUserIdFromToken(token);
            Integer role = jwtUtil.getRoleFromToken(token);
            request.setAttribute("userId", userId);
            request.setAttribute("role", role);
            
            // 检查是否为管理员路径
            if (requestURI.startsWith("/api/admin") && role != 3) {
                response.setStatus(HttpServletResponse.SC_FORBIDDEN);
                response.setContentType("application/json");
                response.getWriter().write("{\"success\": false, \"message\": \"权限不足，需要管理员权限\"}");
                return false;
            }
            
            return true;
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setContentType("application/json");
            response.getWriter().write("{\"success\": false, \"message\": \"token验证失败\"}");
            return false;
        }
    }
}
