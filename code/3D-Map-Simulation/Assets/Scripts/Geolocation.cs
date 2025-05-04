using UnityEngine;

/// <summary>
/// Helper class for geolocation calculations.
/// </summary>
public static class Geolocation
{
    static readonly GeodeticCoords SW = new(49.3563, -112.1609);
    static readonly GeodeticCoords NE = new(49.5363, -111.8609);
    const double WIDTH = 21713, HEIGHT = 20004;

    /* public static readonly GeodeticCoords CENTER = new(49.44620384698518, -112.01097739358276, 0); */
    public static readonly GeodeticCoords CENTER = new(49.3563, -112.1609);
    const float EARTH_RADIUS = 6371000;

    /// <summary>
    /// Converts geodetic coordinates to a Unity world position via Mercator projection, with the height as the y coordinate.
    /// </summary>
    /// <param name="reading"> The WGS84 reading to convert. </param>
    /// <returns> The world position of the reading. </returns>
    public static Vector3 GetWorldPosition(GeodeticCoords geoCoords, Altitude altitude)
    {
        double latDiff = (geoCoords.la - CENTER.la) * (Mathf.PI / 180) * EARTH_RADIUS;
        double lonDiff = (geoCoords.lo - CENTER.lo) * (Mathf.PI / 180) * EARTH_RADIUS * Mathf.Cos((float)CENTER.la * Mathf.PI / 180);

        Vector3 worldPosition = new
        (
            (float)lonDiff,
            (float)altitude.h,
            (float)latDiff
        );

        return worldPosition;
    }
}
