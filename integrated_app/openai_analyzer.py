import os
import json
import pandas as pd
import openai

def extract_ingredients_from_text(text):
    """
    テキストから原材料情報を抽出し、JSON形式で返す
    """
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {
                "ingredients": [],
                "error": "OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。"
            }
            
        openai.api_key = api_key
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """あなたは食品の原材料テキストを分析するエキスパートです。
                    提供されたテキストから原材料リストを抽出し、各原材料について以下の情報を含むJSONを返してください：
                    - 名前
                    - カテゴリ（例：穀物、野菜、調味料など）
                    - 推定栄養成分（100gあたりのカロリー、タンパク質、脂質、炭水化物、塩分）
                    
                    また、原材料は表示順に並べてください（使用量が多い順）。
                    
                    以下の形式でJSON応答を返してください：
                    {
                        "ingredients": [
                            {
                                "name": "原材料名",
                                "category": "カテゴリ",
                                "estimated_nutrition": {
                                    "calories": 数値,
                                    "protein": 数値,
                                    "fat": 数値,
                                    "carbs": 数値,
                                    "salt": 数値
                                }
                            },
                            ...
                        ]
                    }
                    """
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )
        
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
            return result
        except:
            return {
                "ingredients": [],
                "error": "APIレスポンスをJSONとして解析できませんでした。"
            }
            
    except Exception as e:
        return {
            "ingredients": [],
            "error": str(e)
        }

def ingredients_json_to_dataframe(ingredients_data):
    """
    JSON形式の原材料情報をDataFrameに変換
    """
    rows = []
    for i, ingredient in enumerate(ingredients_data.get('ingredients', [])):
        nutrition = ingredient.get('estimated_nutrition', {})
        rows.append({
            'name': ingredient.get('name', ''),
            'category': ingredient.get('category', ''),
            'position': i,  # 表示順（使用量の多い順）
            'calories': nutrition.get('calories', 0),
            'protein': nutrition.get('protein', 0),
            'fat': nutrition.get('fat', 0),
            'carbs': nutrition.get('carbs', 0),
            'salt': nutrition.get('salt', 0)
        })
    
    return pd.DataFrame(rows)
