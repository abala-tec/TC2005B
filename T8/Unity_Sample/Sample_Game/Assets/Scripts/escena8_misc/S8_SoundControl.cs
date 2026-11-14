using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class S8_SoundControl : MonoBehaviour
{
    public AudioClip jump;   // sin static: asi salen en el Inspector
    public AudioClip hit;
    public AudioClip won;

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
}
