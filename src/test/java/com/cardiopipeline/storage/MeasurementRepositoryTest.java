package com.cardiopipeline.storage;

import com.cardiopipeline.model.CardioMeasurement;
import org.junit.jupiter.api.Test;

import java.time.Instant;

class MeasurementRepositoryTest {

    @Test
    void shouldSaveMeasurementToDatabase() {

        CardioMeasurement measurement =
                new CardioMeasurement(
                        1,
                        Instant.now(),
                        "HeartRate",
                        "76"
                );

        MeasurementRepository repository =
                new MeasurementRepository();

        repository.save(measurement);
    }
}