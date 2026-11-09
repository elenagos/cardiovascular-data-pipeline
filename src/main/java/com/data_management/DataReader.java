package com.data_management;
import org.json.JSONObject;
import java.io.IOException;

/**
 * Interface for reading patient data from various sources.
 * Modified to support real-time data streaming via WebSocket.
 */
public interface DataReader {
    /**
     * Connects to a data source and begins continuous data reading.
     * For WebSocket implementation, this starts listening to messages.
     *
     * @param dataStorage the storage where data will be stored
     * @throws IOException if connection fails
     */
    void readData(DataStorage dataStorage) throws IOException;

    /**
     * Disconnects from the data source and stops reading.
     */
    void stopReading();
}