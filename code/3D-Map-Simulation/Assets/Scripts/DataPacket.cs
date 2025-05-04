using System;

/// <summary>
/// Air temperature in degrees Celsius.
/// </summary>
public class Temp
{
    public double t;
}

/// <summary>
/// Air pressure in hPa.
/// </summary>
public class Pressure
{
    public double p;

    public const double SEA_LEVEL_PRESSURE = 1013.25;
}

/// <summary>
/// Altitude in meters, calculated from pressure using the barometric formula.
/// </summary>
[System.Serializable]
public class Altitude
{
    public double h;

    const double exp = 0.1903, denom = 0.0000225577;

    public Altitude(Pressure pressure)
    {
        h = (1 - Math.Pow(pressure.p / Pressure.SEA_LEVEL_PRESSURE, exp)) / denom;
    }

    public Altitude(double altitude)
    {
        h = altitude;
    }
}

/// <summary>
/// A geodetic coordinate in latitude, longitude, and height.
/// </summary>
[System.Serializable]
public struct GeodeticCoords
{
    public double la, lo;

    public GeodeticCoords(double latitude, double longitude)
    {
        this.la = latitude;
        this.lo = longitude;
    }
}
