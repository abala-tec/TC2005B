// Contorno "rayos X" para sprites: solo se dibuja cuando el sprite esta DETRAS de algo (pared).
// Truco: ZTest Greater -> pasa la prueba de profundidad solo si ya hay algo mas cerca de la camara.
Shader "Custom/SpriteXRayOutline"
{
    Properties
    {
        _MainTex ("Sprite", 2D) = "white" {}
        _OutlineColor ("Color contorno", Color) = (1, 0.5, 0, 1)
        _Thickness ("Grosor (texels)", Range(1, 5)) = 2
    }
    SubShader
    {
        // Transparente: se dibuja DESPUES de las paredes, asi el depth buffer ya las tiene
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" "IgnoreProjector"="True" }

        Pass
        {
            ZTest Greater                     // solo donde algo (pared) esta mas cerca que yo
            ZWrite Off                        // no escribo profundidad
            Cull Off                          // los sprites pueden voltearse (flipX)
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);

            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_TexelSize;    // (1/ancho, 1/alto, ancho, alto)
                float4 _OutlineColor;
                float  _Thickness;
            CBUFFER_END

            struct Attributes { float4 posOS : POSITION; float2 uv : TEXCOORD0; };
            struct Varyings   { float4 posCS : SV_POSITION; float2 uv : TEXCOORD0; };

            Varyings vert (Attributes v)
            {
                Varyings o;
                o.posCS = TransformObjectToHClip(v.posOS.xyz);
                o.uv = v.uv;
                return o;
            }

            float AlphaAt(float2 uv) { return SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uv).a; }

            half4 frag (Varyings i) : SV_Target
            {
                float2 d = _MainTex_TexelSize.xy * _Thickness;

                float a    = AlphaAt(i.uv);
                float minA = min(min(AlphaAt(i.uv + float2( d.x, 0)), AlphaAt(i.uv + float2(-d.x, 0))),
                                 min(AlphaAt(i.uv + float2(0,  d.y)), AlphaAt(i.uv + float2(0, -d.y))));

                // 1 en la orilla interior del personaje, 0 en el resto
                float borde = a * (1 - minA);
                clip(borde - 0.1);

                return half4(_OutlineColor.rgb, borde * _OutlineColor.a);
            }
            ENDHLSL
        }
    }
}
