from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        print("Received request:", data)
        
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
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
