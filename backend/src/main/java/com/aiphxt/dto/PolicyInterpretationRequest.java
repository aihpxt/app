package com.aiphxt.dto;

public class PolicyInterpretationRequest {
    private String policy_text;
    private String question;

    public String getPolicy_text() {
        return policy_text;
    }

    public void setPolicy_text(String policy_text) {
        this.policy_text = policy_text;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

}