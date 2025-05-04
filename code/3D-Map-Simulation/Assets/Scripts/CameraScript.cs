using UnityEngine;

public class CameraScript : MonoBehaviour
{
    public float speed = 100;
    public float rotationSpeed = 20;
    const float minX = 0, maxX = 21713, minZ = 0, maxZ = 20004, minY = -1000, maxY = 1000;
    public float sensitivity = 2.0f;
    float rotationX, rotationY;

    void Awake()
    {
        rotationX = transform.rotation.eulerAngles.y;
        rotationY = transform.rotation.eulerAngles.x;
    }

    void Update()
    {
        Vector3 newPosition = transform.position;
        Vector3 moveDir = Vector3.zero;

        if (Input.GetKey(KeyCode.W))
        {
            moveDir += transform.up;
        }
        if (Input.GetKey(KeyCode.S))
        {
            moveDir -= transform.up;
        }
        if (Input.GetKey(KeyCode.A))
        {
            moveDir -= transform.right;
        }
        if (Input.GetKey(KeyCode.D))
        {
            moveDir += transform.right;
        }
        if (Input.GetKey(KeyCode.Q))
        {
            moveDir += transform.forward;
        }
        if (Input.GetKey(KeyCode.E))
        {
            moveDir -= transform.forward;
        }
        if (moveDir != Vector3.zero)
        {
            moveDir.Normalize();
        }

        newPosition += moveDir * speed * Time.deltaTime;
        newPosition.x = Mathf.Clamp(newPosition.x, minX, maxX);
        newPosition.y = Mathf.Clamp(newPosition.y, minY, maxY);
        newPosition.z = Mathf.Clamp(newPosition.z, minZ, maxZ);
        transform.position = newPosition;

        if (Input.GetMouseButton(0))
        {
            float mouseX = Input.GetAxis("Mouse X") * sensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * sensitivity;

            rotationX += mouseX;
            rotationY -= mouseY;
            rotationY = Mathf.Clamp(rotationY, -90f, 90f); // Prevent flipping
            transform.rotation = Quaternion.Euler(rotationY, rotationX, 0);
        }
    }
}
