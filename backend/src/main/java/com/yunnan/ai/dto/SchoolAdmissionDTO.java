package com.yunnan.ai.dto;

import java.math.BigDecimal;

public class SchoolAdmissionDTO {
    private Long id;
    private Long schoolId;
    private Integer year;
    private BigDecimal minScore;
    private BigDecimal avgScore;
    private BigDecimal maxScore;
    private Integer minRank;
    private Integer admissionCount;
    private Integer planCount;
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Long getSchoolId() {
        return schoolId;
    }
    
    public void setSchoolId(Long schoolId) {
        this.schoolId = schoolId;
    }
    
    public Integer getYear() {
        return year;
    }
    
    public void setYear(Integer year) {
        this.year = year;
    }
    
    public BigDecimal getMinScore() {
        return minScore;
    }
    
    public void setMinScore(BigDecimal minScore) {
        this.minScore = minScore;
    }
    
    public BigDecimal getAvgScore() {
        return avgScore;
    }
    
    public void setAvgScore(BigDecimal avgScore) {
        this.avgScore = avgScore;
    }
    
    public BigDecimal getMaxScore() {
        return maxScore;
    }
    
    public void setMaxScore(BigDecimal maxScore) {
        this.maxScore = maxScore;
    }
    
    public Integer getMinRank() {
        return minRank;
    }
    
    public void setMinRank(Integer minRank) {
        this.minRank = minRank;
    }
    
    public Integer getAdmissionCount() {
        return admissionCount;
    }
    
    public void setAdmissionCount(Integer admissionCount) {
        this.admissionCount = admissionCount;
    }
    
    public Integer getPlanCount() {
        return planCount;
    }
    
    public void setPlanCount(Integer planCount) {
        this.planCount = planCount;
    }
}
