using System.ComponentModel;
using UnityEngine;
using UnityEngine.Serialization;   // FormerlySerializedAs: renombrar variables sin perder su valor en el Inspector

[RequireComponent(typeof(AudioSource))]
public class S8_SoundControl : MonoBehaviour
{
    public AudioClip jump;   // sin static: asi salen en el Inspector
    public AudioClip hit;   // when velma gets git by the enemy
    public AudioClip won;
    [FormerlySerializedAs("kick")]
    public AudioClip hachazo;  // cuando el hachazo de velma le pega a un enemigo
    public AudioClip airWush;  // cada vez que velma tira un hachazo (aunque no pegue)
    public AudioClip background;  // musica de background 

    private AudioSource asource;
    private static S8_SoundControl instancia;

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

    public static void play_jump() 
    { 
        instancia.asource.PlayOneShot(instancia.jump); 
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
