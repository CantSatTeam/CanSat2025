using UnityEngine;

public class DataPointScript : MonoBehaviour
{
    [SerializeField] GeodeticCoords coords;
    [SerializeField] Altitude altitude;
    Vector3 originalScale;

    public void Init(GeodeticCoords coords, Altitude altitude)
    {
        this.coords = coords;
        this.altitude = altitude;
        SetPosition();
    }

    void SetPosition()
    {
        transform.position = Geolocation.GetWorldPosition(coords, altitude);
        originalScale = transform.localScale;
    }

    void Start()
    {
        SetPosition();
    }

    void Update()
    {
        transform.position = Geolocation.GetWorldPosition(coords, altitude);

        transform.localScale = originalScale * Mathf.Log(Vector3.Distance(transform.position,  Camera.main.transform.position));
    }
}
