package com.yunnan.ai.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public class SchoolDTO {
    private Long id;
    private String name;
    private String code;
    private Integer type;
    private String typeName;
    private String city;
    private String district;
    private String address;
    private String contact;
    private String website;
    private String intro;
    private String features;
    private List<String> featureList;
    private String logo;
    private List<String> photos;
    private Integer teacherCount;
    private Integer studentCount;
    private BigDecimal area;
    private Integer status;
    private Integer viewCount;
    private LocalDateTime createTime;
    
    private SchoolAdmissionDTO latestAdmission;
    private List<SchoolAdmissionDTO> admissionHistory;
    
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getCode() {
        return code;
    }
    
    public void setCode(String code) {
        this.code = code;
    }
    
    public Integer getType() {
        return type;
    }
    
    public void setType(Integer type) {
        this.type = type;
    }
    
    public String getTypeName() {
        return typeName;
    }
    
    public void setTypeName(String typeName) {
        this.typeName = typeName;
    }
    
    public String getCity() {
        return city;
    }
    
    public void setCity(String city) {
        this.city = city;
    }
    
    public String getDistrict() {
        return district;
    }
    
    public void setDistrict(String district) {
        this.district = district;
    }
    
    public String getAddress() {
        return address;
    }
    
    public void setAddress(String address) {
        this.address = address;
    }
    
    public String getContact() {
        return contact;
    }
    
    public void setContact(String contact) {
        this.contact = contact;
    }
    
    public String getWebsite() {
        return website;
    }
    
    public void setWebsite(String website) {
        this.website = website;
    }
    
    public String getIntro() {
        return intro;
    }
    
    public void setIntro(String intro) {
        this.intro = intro;
    }
    
    public String getFeatures() {
        return features;
    }
    
    public void setFeatures(String features) {
        this.features = features;
    }
    
    public List<String> getFeatureList() {
        return featureList;
    }
    
    public void setFeatureList(List<String> featureList) {
        this.featureList = featureList;
    }
    
    public String getLogo() {
        return logo;
    }
    
    public void setLogo(String logo) {
        this.logo = logo;
    }
    
    public List<String> getPhotos() {
        return photos;
    }
    
    public void setPhotos(List<String> photos) {
        this.photos = photos;
    }
    
    public Integer getTeacherCount() {
        return teacherCount;
    }
    
    public void setTeacherCount(Integer teacherCount) {
        this.teacherCount = teacherCount;
    }
    
    public Integer getStudentCount() {
        return studentCount;
    }
    
    public void setStudentCount(Integer studentCount) {
        this.studentCount = studentCount;
    }
    
    public BigDecimal getArea() {
        return area;
    }
    
    public void setArea(BigDecimal area) {
        this.area = area;
    }
    
    public Integer getStatus() {
        return status;
    }
    
    public void setStatus(Integer status) {
        this.status = status;
    }
    
    public Integer getViewCount() {
        return viewCount;
    }
    
    public void setViewCount(Integer viewCount) {
        this.viewCount = viewCount;
    }
    
    public LocalDateTime getCreateTime() {
        return createTime;
    }
    
    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
    
    public SchoolAdmissionDTO getLatestAdmission() {
        return latestAdmission;
    }
    
    public void setLatestAdmission(SchoolAdmissionDTO latestAdmission) {
        this.latestAdmission = latestAdmission;
    }
    
    public List<SchoolAdmissionDTO> getAdmissionHistory() {
        return admissionHistory;
    }
    
    public void setAdmissionHistory(List<SchoolAdmissionDTO> admissionHistory) {
        this.admissionHistory = admissionHistory;
    }
}
