package com.yunnan.ai.model;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "school_admission")
public class SchoolAdmission {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "school_id", nullable = false)
    private Long schoolId;
    
    @Column(nullable = false)
    private Integer year;
    
    @Column(name = "min_score", nullable = false, precision = 5, scale = 1)
    private BigDecimal minScore;
    
    @Column(name = "avg_score", nullable = false, precision = 5, scale = 1)
    private BigDecimal avgScore;
    
    @Column(name = "max_score", precision = 5, scale = 1)
    private BigDecimal maxScore;
    
    @Column(name = "min_rank", nullable = false)
    private Integer minRank;
    
    @Column(name = "admission_count", nullable = false)
    private Integer admissionCount;
    
    @Column(name = "plan_count")
    private Integer planCount;
    
    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;
    
    @Column(name = "update_time")
    private LocalDateTime updateTime;
    
    @PrePersist
    protected void onCreate() {
        createTime = LocalDateTime.now();
        updateTime = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updateTime = LocalDateTime.now();
    }
    
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
    
    public LocalDateTime getCreateTime() {
        return createTime;
    }
    
    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
    
    public LocalDateTime getUpdateTime() {
        return updateTime;
    }
    
    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }
}
