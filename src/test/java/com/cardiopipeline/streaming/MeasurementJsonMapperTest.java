package com.cardiopipeline.streaming;

import com.cardiopipeline.model.CardioMeasurement;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

class MeasurementJsonMapperTest {

    @Test
    void shouldSerializeAndDeserializeMeasurement() throws Exception {

        CardioMeasurement original = new CardioMeasurement(
                1,
                Instant.parse("2026-10-06T12:00:00Z"),
                "HeartRate",
                "76"
        );

        MeasurementJsonMapper mapper =
                new MeasurementJsonMapper();

        String json = mapper.toJson(original);

        System.out.println(json);

        CardioMeasurement restored =
                mapper.fromJson(json);

        assertEquals(1, restored.getPatientId());
        assertEquals("HeartRate", restored.getType());
        assertEquals("76", restored.getData());

        assertEquals(
                Instant.parse("2026-10-06T12:00:00Z"),
                restored.getTimestamp()
        );
    }
}