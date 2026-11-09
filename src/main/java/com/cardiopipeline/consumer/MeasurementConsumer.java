package com.cardiopipeline.consumer;

import com.cardiopipeline.model.CardioMeasurement;
import com.cardiopipeline.storage.MeasurementRepository;
import com.cardiopipeline.streaming.MeasurementJsonMapper;
import com.cardiopipeline.validation.MeasurementValidator;

public class MeasurementConsumer {

    private final MeasurementJsonMapper mapper =
            new MeasurementJsonMapper();

    private final MeasurementValidator validator =
            new MeasurementValidator();

    private final MeasurementRepository repository =
            new MeasurementRepository();

    public CardioMeasurement consume(String json) {
        try {
            CardioMeasurement measurement =
                    mapper.fromJson(json);

            if (!validator.isValid(measurement)) {
                throw new IllegalArgumentException(
                        "Invalid measurement data"
                );
            }

            repository.save(measurement);

            System.out.println(
                    "Saved measurement: " + measurement
            );

            return measurement;

        } catch (Exception e) {
            throw new IllegalArgumentException(
                    "Failed to consume measurement",
                    e
            );
        }
    }
}