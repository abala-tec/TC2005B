using UnityEngine;

public class S4_CameraFollower : MonoBehaviour
{
    
    public Transform target;  // El gameobject a seguir

    public Vector3 offset = new Vector3(0,5,-10);  // el ofset del objecto a la camara

    public float followspeed = 0.2f;   // la velocidad de seguimiento


    // Usamos LaateUpdate para serguir los objetos despues de 
    // haber sido afectados por fuerzas durante Update()
    void LateUpdate()
    {
        Vector3 goalPosition = target.position + offset;

        // Lerp interpolates between the cam current pos to the goal position
        Vector3 smoothedPosition = Vector3.Lerp(transform.position, goalPosition, followspeed);

        transform.position = smoothedPosition;
    }
}
