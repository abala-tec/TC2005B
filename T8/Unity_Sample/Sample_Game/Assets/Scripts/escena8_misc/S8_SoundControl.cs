using System.ComponentModel;
using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class S8_SoundControl : MonoBehaviour
{
    public AudioClip jump;   // sin static: asi salen en el Inspector
    public AudioClip hit;   // when velma gets git by the enemy
    public AudioClip won;
    public AudioClip kick;  // when velma kicks an enemy and hits
    public AudioClip airWush;  // everytime velma kicks 

    private AudioSource asource;
    private static S8_SoundControl instancia;

    void Awake()
    {
        instancia = this;
        asource = GetComponent<AudioSource>();
    }

    public static void play_jump() 
    { 
        instancia.asource.PlayOneShot(instancia.jump); 
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
