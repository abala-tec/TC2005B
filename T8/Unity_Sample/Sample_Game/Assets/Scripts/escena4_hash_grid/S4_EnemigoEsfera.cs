using Unity.VisualScripting;
using UnityEngine;
using System;

public class S4_EnemigoEsfera : MonoBehaviour
{
    public Transform cubo;
    private Vector3[] esquinas;  //areglo de vector3 para guardar las esquinas
    public int indiceObjetivo;
    public float velocidad = 5.0f;
    public float distanciaContacto = 1.1f;  // distancia para saber si el cubo toco a la esfera
    public float anguloPisoton = 60f;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        esquinas = new Vector3[4];
        esquinas[0] = new Vector3(transform.position.x-3.5f, 0.5f, transform.position.z-3.5f);
        esquinas[1] = new Vector3(transform.position.x+3.5f, 0.5f, transform.position.z-3.5f);
        esquinas[2] = new Vector3(transform.position.x+3.5f, 0.5f, transform.position.z+3.5f);
        esquinas[3] = new Vector3(transform.position.x-3.5f, 0.5f, transform.position.z+3.5f);

        // setup de la primera esquina
        NewRandom();
        transform.position = esquinas[indiceObjetivo];

        InvokeRepeating("NewRandom", 0f, 5f);  // cambiar de esquina cada 5 segundos
    }

    void NewRandom()
    {
        indiceObjetivo = UnityEngine.Random.Range(0, 4); 
    }

    static float Longitud(Vector3 v)
    {
        return (float)Math.Sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    }

    static Vector3 Normalizar(Vector3 v)
    {
        float longitud = Longitud(v);
        if (longitud < 0.0001f) { 
            return new Vector3(0f, 0f, 0f);
        }
        return new Vector3(v.x / longitud, v.y / longitud, v.z / longitud);
    }

    //Moviendo la esfera de esquina a esquina
    void MoverEsfera()
    {
        Vector3 objetivo = esquinas[indiceObjetivo];
        Vector3 hacia = objetivo - transform.position;
        float distancia = Longitud(hacia);

        if (distancia < 0.1f)
        {
            // Elige otra esquina distinta: suma 1, 2 o 3 y da la vuelta
            indiceObjetivo = (indiceObjetivo + UnityEngine.Random.Range(1, 4)) % 4;
            return;
        }

        Vector3 direccion = Normalizar(hacia);
        float paso = velocidad * Time.deltaTime;

        transform.position = new Vector3(
            transform.position.x + direccion.x * paso,
            transform.position.y,                       // la altura no cambia
            transform.position.z + direccion.z * paso
        );
    }

    // bool Contacto()
    // {
    //     Vector3 haciaCubo = cubo.position - transform.position;
    //     float distanciaCubo = Longitud(haciaCubo);

    //     if (distanciaCubo <= distanciaContacto)
    //     {
    //         return true;
    //     }
    //     return false;
    // }

    bool Pisoton()
    {
        Vector3 haciaCubo = cubo.position - transform.position;
        float dx = haciaCubo.x;
        float dy = haciaCubo.y;
        float dz = haciaCubo.z;

        float horizontal = (float) Math.Sqrt(dx*dx + dz*dz);  // distancia horizontal
        float angulo = (float)(Math.Atan2(dy, horizontal) * 180.0 / Math.PI); // angulo vertical

        if (angulo >= anguloPisoton && horizontal <= distanciaContacto){
            Debug.Log("PISOTON");
            Reset();
            return true;
        }
        return false;

    }

    // resetea la posicion de la esfera a una nueva esquina
    void Reset()
    {
        NewRandom();
        transform.position = esquinas[indiceObjetivo];
    }

    // Update is called once per frame
    void Update()
    {
        MoverEsfera();
        // Contacto();
        Pisoton();

    }

    
    
}
