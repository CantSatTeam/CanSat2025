using UnityEngine;

public class BillboardScript : MonoBehaviour
{
    void Update()
    {
        Vector3 dir = Camera.main.transform.position - transform.position;
        Quaternion rotation = Quaternion.LookRotation(dir);
        transform.rotation = rotation;
    }
}
