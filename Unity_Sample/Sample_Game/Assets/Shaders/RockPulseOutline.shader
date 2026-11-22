// Contorno rojo palpitante alrededor de la piedra (cuando tiene a Velma atrapada).
// Tecnica "inverted hull": dibuja la malla otra vez un poco mas grande y SOLO sus caras traseras (Cull Front).
// La piedra normal tapa el centro, asi que solo se ve la orilla que sobresale = contorno.
Shader "Custom/RockPulseOutline"
{
    Properties
    {
        _OutlineColor ("Color contorno", Color) = (1, 0, 0, 1)
        _WidthMin ("Grosor minimo", Range(0, 0.5)) = 0.04
        _WidthMax ("Grosor maximo", Range(0, 0.5)) = 0.12
        _PulseSpeed ("Velocidad del pulso", Range(0, 20)) = 6
        _Center ("Centro (mundo, lo pone el script)", Vector) = (0, 0, 0, 0)
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" }

        Pass
        {
            Cull Front                        // solo caras traseras del casco agrandado
            ZWrite Off
            ZTest LEqual
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _OutlineColor;
                float  _WidthMin;
                float  _WidthMax;
                float  _PulseSpeed;
                float4 _Center;
            CBUFFER_END

            struct Attributes { float4 posOS : POSITION; };
            struct Varyings   { float4 posCS : SV_POSITION; float pulso : TEXCOORD0; };

            Varyings vert (Attributes v)
            {
                Varyings o;

                // pulso de 0 a 1 que sube y baja con el tiempo
                float pulso = 0.5 + 0.5 * sin(_Time.y * _PulseSpeed);
                float grosor = lerp(_WidthMin, _WidthMax, pulso);

                // agranda la malla desde su centro (funciona bien con cajas, sin huecos en las esquinas)
                float3 posWS = TransformObjectToWorld(v.posOS.xyz);
                posWS = _Center.xyz + (posWS - _Center.xyz) * (1 + grosor);

                o.posCS = TransformWorldToHClip(posWS);
                o.pulso = pulso;
                return o;
            }

            half4 frag (Varyings i) : SV_Target
            {
                // tambien palpita la intensidad
                float a = lerp(0.35, 1.0, i.pulso) * _OutlineColor.a;
                return half4(_OutlineColor.rgb, a);
            }
            ENDHLSL
        }
    }
}
