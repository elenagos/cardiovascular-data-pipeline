package com.cardiopipeline.streaming;

import com.cardiopipeline.model.CardioMeasurement;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

public class MeasurementJsonMapper {

    private final ObjectMapper objectMapper;

    public MeasurementJsonMapper() {
        objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
    }

    public String toJson(CardioMeasurement measurement) throws Exception {
        return objectMapper.writeValueAsString(measurement);
    }

    public CardioMeasurement fromJson(String json) throws Exception {
        return objectMapper.readValue(json, CardioMeasurement.class);
    }
}