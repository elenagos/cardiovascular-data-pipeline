package com.cardio_generator.outputs;

import com.cardiopipeline.model.CardioMeasurement;
import com.cardiopipeline.streaming.MeasurementJsonMapper;

import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;

import java.net.InetSocketAddress;
import java.time.Instant;
import java.util.Collection;

/**
 * An OutputStrategy implementation that broadcasts patient data
 * to connected WebSocket clients as JSON.
 */
public class WebSocketOutputStrategy implements OutputStrategy {

    private static WebSocketServer server;

    private final MeasurementJsonMapper jsonMapper =
            new MeasurementJsonMapper();

    /**
     * Creates a WebSocket output strategy on the specified port.
     *
     * @param port TCP port to listen on
     */
    public WebSocketOutputStrategy(int port) {
        this(createDefaultServer(port));
    }

    /**
     * Package-private constructor used for tests.
     *
     * @param server WebSocket server implementation
     */
    WebSocketOutputStrategy(WebSocketServer server) {
        WebSocketOutputStrategy.server = server;

        System.out.println(
                "WebSocket server created on port: "
                        + server.getPort()
                        + ", listening for connections..."
        );

        server.start();
    }

    /**
     * Returns the current WebSocket server.
     */
    public WebSocketServer getServer() {
        return server;
    }

    /**
     * Creates the default WebSocket server.
     *
     * @param port port to bind to
     * @return WebSocketServer instance
     */
    public static WebSocketServer createDefaultServer(int port) {
        return new SimpleWebSocketServer(
                new InetSocketAddress(port)
        );
    }

    /**
     * Converts generated health data into a CardioMeasurement,
     * serializes it to JSON and broadcasts it to all clients.
     */
    @Override
    public void output(
            int patientId,
            long timestamp,
            String label,
            String data
    ) {

        try {
            CardioMeasurement measurement =
                    new CardioMeasurement(
                            patientId,
                            Instant.ofEpochMilli(timestamp),
                            label,
                            data
                    );

            String message =
                    jsonMapper.toJson(measurement);

            for (WebSocket connection : server.getConnections()) {
                connection.send(message);
            }

            System.out.println(
                    "Broadcasting JSON: " + message
            );

        } catch (Exception e) {
            throw new IllegalStateException(
                    "Failed to serialize measurement to JSON",
                    e
            );
        }
    }

    /**
     * Basic WebSocket server implementation.
     */
    private static class SimpleWebSocketServer
            extends WebSocketServer {

        public SimpleWebSocketServer(
                InetSocketAddress address
        ) {
            super(address);
        }

        @Override
        public void onOpen(
                WebSocket connection,
                ClientHandshake handshake
        ) {
            System.out.println(
                    "New connection: "
                            + connection.getRemoteSocketAddress()
            );
        }

        @Override
        public void onClose(
                WebSocket connection,
                int code,
                String reason,
                boolean remote
        ) {
            System.out.println(
                    "Closed connection: "
                            + connection.getRemoteSocketAddress()
            );
        }

        @Override
        public void onMessage(
                WebSocket connection,
                String message
        ) {
            System.out.println(
                    "Received message from client: " + message
            );
        }

        @Override
        public void onError(
                WebSocket connection,
                Exception exception
        ) {
            System.err.println(
                    "WebSocket server error: "
                            + exception.getMessage()
            );

            exception.printStackTrace();
        }

        @Override
        public void onStart() {
            System.out.println(
                    "WebSocket server started successfully"
            );
        }

        @Override
        public Collection<WebSocket> getConnections() {
            return super.getConnections();
        }
    }
}