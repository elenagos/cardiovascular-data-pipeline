package com.cardiopipeline.storage;

import com.cardiopipeline.model.CardioMeasurement;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;

public class MeasurementRepository {

    private static final String INSERT_SQL =
            "INSERT INTO measurements (" +
                    "patient_id, " +
                    "recorded_at, " +
                    "measurement_type, " +
                    "measurement_data" +
                    ") VALUES (?, ?, ?, ?)";

    public void save(CardioMeasurement measurement) {

        try (
                Connection connection =
                        DatabaseConnection.getConnection();

                PreparedStatement statement =
                        connection.prepareStatement(INSERT_SQL)
        ) {

            statement.setInt(
                    1,
                    measurement.getPatientId()
            );

            statement.setTimestamp(
                    2,
                    Timestamp.from(
                            measurement.getTimestamp()
                    )
            );

            statement.setString(
                    3,
                    measurement.getType()
            );

            statement.setString(
                    4,
                    measurement.getData()
            );

            statement.executeUpdate();

        } catch (SQLException e) {
            throw new IllegalStateException(
                    "Failed to save measurement",
                    e
            );
        }
    }
}