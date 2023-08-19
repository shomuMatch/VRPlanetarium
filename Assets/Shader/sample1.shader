Shader "CustomSkybox/StarGazerSkybox"
{
    Properties
    {
        _radiusCoefficient("Radius Coefficient", Float) = 2000
        _brightnessCoefficient("Brightness Coefficient", Float) = 2
    }
    SubShader
    {
        Tags
        {
            "RenderType"="Background"
            "Queue"="Background"
            "PreviewType"="SkyBox"
        }
        Pass
        {
            ZWrite Off
            Cull Off

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            struct appdata
            {
                float4 vertex : POSITION;
                float3 texcoord : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex : SV_POSITION;
                float3 texcoord : TEXCOORD0;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.texcoord = v.texcoord;
                return o;
            }

            float _radiusCoefficient;
            float _brightnessCoefficient;

            struct Star
            {
                float3 direction;
                fixed3 color;
                float magnitude;
            };

            Star createStar(float3 dir, fixed3 col, float mag)
            {
                Star result;
                result.direction = dir;
                result.color = col;
                result.magnitude = mag;
                return result;
            }

            static const Star stars[2] = {
                createStar(float3(1, 1, 0), fixed3(1, 1, 1), 0.5),
                createStar(float3(0, 1, 1), fixed3(1, 0.5, 0.5), 1),
            };

            // 背景色を定義
            fixed4 drawBackground()
            {
                return fixed4(0, 0, 0, 1);
            }

            // 星を描画
            fixed4 drawStars(float3 dir)
            {
                float3 o = float3(0, 0, 0);
                for (int i = 0; i < 2; i++)
                {
                    float3 direction = normalize(stars[i].direction);
                    fixed3 color = normalize(stars[i].color);
                    float angle = dot(dir, direction);
                    o += color * pow(max(0.0, angle), _radiusCoefficient * (stars[i].magnitude + 2)) * pow(2.5, -1 * stars[i].magnitude) * _brightnessCoefficient;
                }
                return float4(o, 1);
            }

            // 各ピクセルごとの色を決定
            fixed4 frag(v2f i) : SV_Target
            {
                return drawBackground() + drawStars(i.texcoord);
            }
            ENDCG
        }
    }
}
