package com.cardio_generator.outputs;

import com.cardiopipeline.consumer.MeasurementConsumer;
import com.cardiopipeline.model.CardioMeasurement;
import com.cardiopipeline.streaming.MeasurementJsonMapper;
import com.data_management.DataStorage;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.Timer;
import java.util.TimerTask;

/**
 * WebSocket client that receives real-time cardiovascular data.
 *
 * Preferred pipeline:
 *
 * WebSocket
 * -> MeasurementConsumer
 * -> MeasurementValidator
 * -> MeasurementRepository
 * -> PostgreSQL
 *
 * A legacy DataStorage constructor is kept temporarily so older
 * tests and code can continue to compile during migration.
 */
public class HealthDataWebSocketClient extends WebSocketClient {

    private static final int RECONNECT_DELAY_MS = 5000;

    private final URI serverUri;
    private final MeasurementConsumer consumer;
    private final DataStorage dataStorage;

    private final MeasurementJsonMapper jsonMapper =
            new MeasurementJsonMapper();

    private boolean reconnecting = false;

    /**
     * Constructor for the new PostgreSQL pipeline.
     *
     * @param serverUri WebSocket server URI
     * @param consumer consumer responsible for parsing,
     *                 validating and storing measurements
     */
    public HealthDataWebSocketClient(
            URI serverUri,
            MeasurementConsumer consumer
    ) {
        super(serverUri);

        this.serverUri = serverUri;
        this.consumer = consumer;
        this.dataStorage = null;
    }

    /**
     * Legacy constructor kept for compatibility with existing code/tests.
     *
     * @param serverUri WebSocket server URI
     * @param storage legacy DataStorage instance
     */
    public HealthDataWebSocketClient(
            URI serverUri,
            DataStorage storage
    ) {
        super(serverUri);

        this.serverUri = serverUri;
        this.dataStorage = storage;
        this.consumer = null;
    }

    @Override
    public void onOpen(ServerHandshake handshakeData) {
        System.out.println(
                "Connected to WebSocket server: " + serverUri
        );

        reconnecting = false;
    }

    /**
     * Processes incoming JSON messages.
     */
    @Override
    public void onMessage(String message) {

        try {

            /*
             * New pipeline.
             */
            if (consumer != null) {

                consumer.consume(message);

                System.out.println(
                        "Processed measurement: " + message
                );

                return;
            }

            /*
             * Legacy compatibility path.
             */
            if (dataStorage != null) {

                CardioMeasurement measurement =
                        jsonMapper.fromJson(message);

                double numericValue =
                        Double.parseDouble(
                                measurement.getData()
                        );

                dataStorage.addPatientData(
                        measurement.getPatientId(),
                        numericValue,
                        measurement.getType(),
                        measurement
                                .getTimestamp()
                                .toEpochMilli()
                );

                System.out.println(
                        "Stored measurement in legacy DataStorage: "
                                + message
                );
            }

        } catch (Exception e) {

            System.err.println(
                    "Failed to process WebSocket message: "
                            + message
            );

            e.printStackTrace();
        }
    }

    @Override
    public void onClose(
            int code,
            String reason,
            boolean remote
    ) {

        System.out.println(
                "Connection closed: " + reason
        );

        attemptReconnect();
    }

    @Override
    public void onError(Exception exception) {

        System.err.println(
                "WebSocket error: "
                        + exception.getMessage()
        );

        attemptReconnect();
    }

    /**
     * Schedules a reconnect attempt.
     */
    private synchronized void attemptReconnect() {

        if (reconnecting) {
            return;
        }

        reconnecting = true;

        System.out.println(
                "Attempting to reconnect in "
                        + (RECONNECT_DELAY_MS / 1000)
                        + " seconds..."
        );

        Timer timer = new Timer(true);

        timer.schedule(
                new TimerTask() {

                    @Override
                    public void run() {
                        performReconnect();
                    }

                },
                RECONNECT_DELAY_MS
        );
    }

    /**
     * Creates a fresh client instance and reconnects.
     *
     * This method intentionally has a different name from
     * WebSocketClient.reconnect().
     */
    private void performReconnect() {

        try {

            HealthDataWebSocketClient newClient;

            if (consumer != null) {

                newClient =
                        new HealthDataWebSocketClient(
                                serverUri,
                                consumer
                        );

            } else {

                newClient =
                        new HealthDataWebSocketClient(
                                serverUri,
                                dataStorage
                        );
            }

            newClient.connect();

        } catch (Exception e) {

            System.err.println(
                    "Failed to reconnect: "
                            + e.getMessage()
            );

            reconnecting = false;
        }
    }
}