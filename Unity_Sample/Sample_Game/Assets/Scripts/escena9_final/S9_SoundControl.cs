using System.ComponentModel;
using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class S9_SoundControl : MonoBehaviour
{
    public AudioClip hit;   // sin static: asi salen en el Inspector
    public AudioClip won;
    public AudioClip kick;  // when velma kicks an enemy and hits
    public AudioClip airWush;  // everytime velma kicks 
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

    public static void play_kick()
    {
        instancia.asource.PlayOneShot(instancia.kick);
    }

    public static void play_airWush()
    {
        instancia.asource.PlayOneShot(instancia.airWush);
    }
}
