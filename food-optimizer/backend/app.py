import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai_analyzer
import quantum_optimizer

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_ingredients():
    data = request.json
    ingredient_text = data.get('ingredient_text', '')
    
    ingredients_info = openai_analyzer.extract_ingredients_from_text(ingredient_text)
    
    if 'error' in ingredients_info:
        return jsonify({'error': ingredients_info['error']}), 400
        
    ingredients_df = openai_analyzer.ingredients_json_to_dataframe(ingredients_info)
    
    target_nutrition = data.get('target_nutrition', {
        'calories': 299.0,
        'protein': 12.0,
        'fat': 7.4,
        'carbs': 46.4,
        'salt': 0.0,
        'total_amount': 100.0
    })
    
    result = quantum_optimizer.optimize_ingredients(ingredients_df, target_nutrition)
    
    return jsonify({
        'ingredients': ingredients_info,
        'optimization_result': result
    })
    
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})
    
if __name__ == '__main__':
    app.run(debug=True)
