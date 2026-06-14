package com.aiphxt.dto;

import java.util.List;

public class VolunteerPlanRequest {
    private double score;
    private int rank;
    private String district = "昆明";
    private List<Integer> schools;

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }

    public int getRank() {
        return rank;
    }

    public void setRank(int rank) {
        this.rank = rank;
    }

    public String getDistrict() {
        return district;
    }

    public void setDistrict(String district) {
        this.district = district;
    }

    public List<Integer> getSchools() {
        return schools;
    }

    public void setSchools(List<Integer> schools) {
        this.schools = schools;
    }

}