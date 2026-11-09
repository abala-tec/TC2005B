using Unity.VisualScripting;
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEditor;

public class S6_EnemigoCilindro : MonoBehaviour
{
    public Transform cubo;
    public float velocidad = 5.0f;
    private List<Vector2Int> camino;       // casillas por recorrer
    private float tiempoRecalculo = 0f;
    public float cadaCuanto = 0.25f;       // cada cuántos segundos recalcula el camino

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }


    void Perseguir()
    {
        S6_Grid grid = S6_Grid.Instancia;

        // recalcular el camino cada 0.25 s (no en cada frame: es innecesario)
        tiempoRecalculo -= Time.deltaTime;
        if (tiempoRecalculo <= 0f)
        {
            tiempoRecalculo = cadaCuanto;
            camino = grid.BuscarCamino(grid.MundoACelda(transform.position),
                                       grid.MundoACelda(cubo.position));
        }

        // UnityEngine.Debug.Log(camino);
        if (camino == null || camino.Count == 0) return;   // sin camino: se queda quieto

        
        // caminar hacia la siguiente casilla del camino
        Vector3 objetivo = grid.CeldaAMundo(camino[0]);
        objetivo.y = transform.position.y;                  // la altura no cambia
        transform.position = Vector3.MoveTowards(transform.position, objetivo, velocidad * Time.deltaTime);
    }


    // Update is called once per frame
    void Update()
    {
        Perseguir();
    }

    void OnDrawGizmos()
    {
        S6_Grid grid = S6_Grid.Instancia;

        if (camino == null || camino.Count == 0) return;
        for (int i = 0; i < camino.Count - 1; i++)
        {
            Gizmos.color = new Color(1, 1, 0, 0.9f);
            Gizmos.DrawLine(
                grid.CeldaAMundo(camino[i]) + Vector3.up,
                grid.CeldaAMundo(camino[i + 1]) + Vector3.up
            );
        }
    }

    
    
}
