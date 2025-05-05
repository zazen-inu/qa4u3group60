import json
import os
import openai_analyzer
import quantum_optimizer

def handler(event, context):
    try:
        body = json.loads(event['body'])
        ingredient_text = body.get('ingredient_text', '')
        target_nutrition = body.get('target_nutrition', {
            'calories': 299.0,
            'protein': 12.0,
            'fat': 7.4,
            'carbs': 46.4,
            'salt': 0.0,
            'total_amount': 100.0
        })
        
        ingredients_info = openai_analyzer.extract_ingredients_from_text(ingredient_text)
        
        if 'error' in ingredients_info:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': ingredients_info['error']})
            }
            
        ingredients_df = openai_analyzer.ingredients_json_to_dataframe(ingredients_info)
        
        result = quantum_optimizer.optimize_ingredients(ingredients_df, target_nutrition)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'ingredients': ingredients_info,
                'optimization_result': result
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
