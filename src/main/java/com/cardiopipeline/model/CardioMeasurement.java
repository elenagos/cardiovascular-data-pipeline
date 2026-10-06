package com.cardiopipeline.model;

import java.time.Instant;

public class CardioMeasurement {

    private int patientId;
    private Instant timestamp;
    private String type;
    private String data;

    public CardioMeasurement() {
    }

    public CardioMeasurement(
            int patientId,
            Instant timestamp,
            String type,
            String data
    ) {
        this.patientId = patientId;
        this.timestamp = timestamp;
        this.type = type;
        this.data = data;
    }

    public int getPatientId() {
        return patientId;
    }

    public void setPatientId(int patientId) {
        this.patientId = patientId;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Instant timestamp) {
        this.timestamp = timestamp;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }

    @Override
    public String toString() {
        return "CardioMeasurement{" +
                "patientId=" + patientId +
                ", timestamp=" + timestamp +
                ", type='" + type + '\'' +
                ", data='" + data + '\'' +
                '}';
    }
}