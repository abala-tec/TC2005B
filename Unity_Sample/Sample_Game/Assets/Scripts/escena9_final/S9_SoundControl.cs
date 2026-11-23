using System.ComponentModel;
using UnityEngine;
using UnityEngine.Serialization;

[RequireComponent(typeof(AudioSource))]
public class S9_SoundControl : MonoBehaviour
{
    public AudioClip hit;   // sin static: asi salen en el Inspector
    public AudioClip won;
    [FormerlySerializedAs("kick")]
    public AudioClip hachazo;  // cuando el hachazo de velma le pega a un enemigo
    public AudioClip airWush;  // cada vez que velma tira un hachazo (aunque no pegue)
    public AudioClip background;  // musica de background 

    private AudioSource asource;
    private static S9_SoundControl instancia;

    void Awake()
    {
        instancia = this;
        asource = GetComponent<AudioSource>();

        if (background != null)
        {
            asource.clip = background;
            asource.loop = true;
            asource.Play();
        }
    }

    public static void play_hit()  
    { 
        instancia.asource.PlayOneShot(instancia.hit); 
    }

    public static void play_hachazo()
    {
        instancia.asource.PlayOneShot(instancia.hachazo);
    }

    public static void play_airWush()
    {
        instancia.asource.PlayOneShot(instancia.airWush);
    }
}
