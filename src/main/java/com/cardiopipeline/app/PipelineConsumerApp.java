package com.cardiopipeline.app;

import com.cardio_generator.outputs.HealthDataWebSocketClient;
import com.cardiopipeline.consumer.MeasurementConsumer;

import java.net.URI;

public class PipelineConsumerApp {

    public static void main(String[] args) throws Exception {

        MeasurementConsumer consumer =
                new MeasurementConsumer();

        URI serverUri =
                new URI("ws://localhost:8080");

        HealthDataWebSocketClient client =
                new HealthDataWebSocketClient(
                        serverUri,
                        consumer
                );

        System.out.println(
                "Connecting consumer to " + serverUri
        );

        client.connectBlocking();

        System.out.println(
                "Consumer connected and listening..."
        );
    }
}