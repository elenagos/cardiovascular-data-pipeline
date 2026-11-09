package com.cardiopipeline.validation;

import com.cardiopipeline.model.CardioMeasurement;

public class MeasurementValidator {

    public boolean isValid(CardioMeasurement measurement) {

        if (measurement == null) {
            return false;
        }

        if (measurement.getPatientId() <= 0) {
            return false;
        }

        if (measurement.getTimestamp() == null) {
            return false;
        }

        if (measurement.getType() == null ||
                measurement.getType().isBlank()) {
            return false;
        }

        if (measurement.getData() == null ||
                measurement.getData().isBlank()) {
            return false;
        }

        return true;
    }
}