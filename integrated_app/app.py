from flask import Flask, request, jsonify, render_template
import json
import os
import pandas as pd
import traceback

try:
    import openai_analyzer
    import quantum_optimizer
    MOCK_MODE = False
except ImportError:
    print("Warning: openai_analyzer or quantum_optimizer modules not found. Using mock data.")
    MOCK_MODE = True

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        print("Received request:", data)
        
        ingredient_text = data.get('ingredient_text', '')
        target_nutrition = data.get('target_nutrition', {
            'calories': 299.0,
            'protein': 12.0,
            'fat': 7.4,
            'carbs': 46.4,
            'salt': 0.0,
            'total_amount': 100.0
        })
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key and not MOCK_MODE:
            print("Warning: OPENAI_API_KEY not set. Using mock data.")
            return use_mock_data()
            
        if MOCK_MODE:
            print("Using mock data (modules not imported).")
            return use_mock_data()
            
        try:
            ingredients_info = openai_analyzer.extract_ingredients_from_text(ingredient_text)
            
            if 'error' in ingredients_info:
                print(f"OpenAI API error: {ingredients_info['error']}")
                return use_mock_data()
                
            ingredients_df = openai_analyzer.ingredients_json_to_dataframe(ingredients_info)
            
            result = quantum_optimizer.optimize_ingredients(ingredients_df, target_nutrition)
            
            return jsonify({
                'ingredients': ingredients_info,
                'optimization_result': result
            })
            
        except Exception as e:
            print(f"Error in API processing: {str(e)}")
            traceback.print_exc()
            return use_mock_data()
            
    except Exception as e:
        print("Error:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def use_mock_data():
    """モックデータを返す（APIキーがない場合やエラー時）"""
    response = {
        'ingredients': {
            'ingredients': [
                {
                    'name': 'きなこ',
                    'category': '豆類',
                    'estimated_nutrition': {
                        'calories': 400,
                        'protein': 35,
                        'fat': 20,
                        'carbs': 30,
                        'salt': 0
                    }
                },
                {
                    'name': '水飴',
                    'category': '糖類',
                    'estimated_nutrition': {
                        'calories': 300,
                        'protein': 0,
                        'fat': 0,
                        'carbs': 75,
                        'salt': 0
                    }
                },
                {
                    'name': '砂糖',
                    'category': '糖類',
                    'estimated_nutrition': {
                        'calories': 400,
                        'protein': 0,
                        'fat': 0,
                        'carbs': 100,
                        'salt': 0
                    }
                }
            ]
        },
        'optimization_result': {
            'proportions': {
                'きなこ': 40,
                '水飴': 35,
                '砂糖': 25
            },
            'calculated_nutrition': {
                'per_gram': {
                    'calories': 3.65,
                    'protein': 14.0,
                    'fat': 8.0,
                    'carbs': 62.25,
                    'salt': 0
                },
                'total': {
                    'calories': 365,
                    'protein': 14.0,
                    'fat': 8.0,
                    'carbs': 62.25,
                    'salt': 0
                }
            }
        }
    }
    
    return jsonify(response)

@app.route('/api_status', methods=['GET'])
def api_status():
    """APIの状態を確認するエンドポイント"""
    api_key = os.environ.get('OPENAI_API_KEY')
    status = {
        'openai_api_key': 'configured' if api_key else 'not_configured',
        'modules_imported': not MOCK_MODE,
        'mock_mode': MOCK_MODE
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
