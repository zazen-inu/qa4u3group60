import numpy as np
from neal import SimulatedAnnealingSampler as SASampler
from dimod import BinaryQuadraticModel

def optimize_ingredients(ingredients_df, target_nutrition):
    """
    量子アニーリングを使用して原材料の最適な配合比率を計算
    """
    num_ingredients = len(ingredients_df)
    
    target_calories = target_nutrition.get('calories', 0)
    target_protein = target_nutrition.get('protein', 0)
    target_fat = target_nutrition.get('fat', 0)
    target_carbs = target_nutrition.get('carbs', 0)
    
    ingredient_nutrition_per_g = {}
    for i, row in ingredients_df.iterrows():
        ingredient_key = f'ingredient{i+1}'
        ingredient_nutrition_per_g[ingredient_key] = {
            'calories': row['calories'] / 100,  # 100gあたりから1gあたりに変換
            'protein': row['protein'] / 100,
            'fat': row['fat'] / 100,
            'carbs': row['carbs'] / 100,
            'salt': row['salt'] / 100,
            'name': row['name']
        }
    
    total_weight = target_nutrition.get('total_amount', 100)
    target_calories_g = target_calories / total_weight
    target_protein_g = target_protein / total_weight
    target_fat_g = target_fat / total_weight
    target_carbs_g = target_carbs / total_weight
    
    for key in ingredient_nutrition_per_g:
        data = ingredient_nutrition_per_g[key]
        data['calories'] = data['calories'] / target_calories_g if target_calories_g > 0 else 0
        data['protein'] = data['protein'] / target_protein_g if target_protein_g > 0 else 0
        data['fat'] = data['fat'] / target_fat_g if target_fat_g > 0 else 0
        data['carbs'] = data['carbs'] / target_carbs_g if target_carbs_g > 0 else 0
    
    A = 1.0  # カロリー誤差
    B = 1.0  # タンパク質誤差
    C = 1.0  # 脂質誤差
    D = 1.0  # 炭水化物誤差
    F = 100.0  # 合計100%制約
    
    num_bits_per_ingredient = 16
    bqm = BinaryQuadraticModel({}, {}, offset=0.0, vartype='BINARY')
    q = {}  # q[ingredient_index][bit_index] でアクセス
    
    for i in range(num_ingredients):
        q[i] = [f'q_{i}_{j}' for j in range(num_bits_per_ingredient)]
        for j in range(num_bits_per_ingredient):
            bqm.add_variable(q[i][j])
    
    def get_weight(i, j):
        return 1.0 / (2 ** (j + 1))
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            weight_i_j = get_weight(i, j)
            bqm.add_variable(q[i][j], F * weight_i_j * weight_i_j)
            for k in range(j+1, num_bits_per_ingredient):
                weight_i_k = get_weight(i, k)
                bqm.add_interaction(q[i][j], q[i][k], 2 * F * weight_i_j * weight_i_k)
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            weight_i_j = get_weight(i, j)
            for m in range(i+1, num_ingredients):
                for n in range(num_bits_per_ingredient):
                    weight_m_n = get_weight(m, n)
                    bqm.add_interaction(q[i][j], q[m][n], 2 * F * weight_i_j * weight_m_n)
    
    ingredient_keys = [f'ingredient{i+1}' for i in range(num_ingredients)]
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            cal_i = ingredient_nutrition_per_g[ingredient_keys[i]]['calories']
            weight_i_j = get_weight(i, j)
            error_term = A * (cal_i * weight_i_j) * (cal_i * weight_i_j - 2 * weight_i_j)
            bqm.add_variable(q[i][j], error_term)
            
            for k in range(j+1, num_bits_per_ingredient):
                weight_i_k = get_weight(i, k)
                error_term = 2 * A * (cal_i * weight_i_j) * (cal_i * weight_i_k)
                bqm.add_interaction(q[i][j], q[i][k], error_term)
                
            for m in range(i+1, num_ingredients):
                cal_m = ingredient_nutrition_per_g[ingredient_keys[m]]['calories']
                for n in range(num_bits_per_ingredient):
                    weight_m_n = get_weight(m, n)
                    error_term = 2 * A * (cal_i * weight_i_j) * (cal_m * weight_m_n)
                    bqm.add_interaction(q[i][j], q[m][n], error_term)
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            prot_i = ingredient_nutrition_per_g[ingredient_keys[i]]['protein']
            weight_i_j = get_weight(i, j)
            error_term = B * (prot_i * weight_i_j) * (prot_i * weight_i_j - 2 * weight_i_j)
            bqm.add_variable(q[i][j], error_term)
            
            for k in range(j+1, num_bits_per_ingredient):
                weight_i_k = get_weight(i, k)
                error_term = 2 * B * (prot_i * weight_i_j) * (prot_i * weight_i_k)
                bqm.add_interaction(q[i][j], q[i][k], error_term)
                
            for m in range(i+1, num_ingredients):
                prot_m = ingredient_nutrition_per_g[ingredient_keys[m]]['protein']
                for n in range(num_bits_per_ingredient):
                    weight_m_n = get_weight(m, n)
                    error_term = 2 * B * (prot_i * weight_i_j) * (prot_m * weight_m_n)
                    bqm.add_interaction(q[i][j], q[m][n], error_term)
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            fat_i = ingredient_nutrition_per_g[ingredient_keys[i]]['fat']
            weight_i_j = get_weight(i, j)
            error_term = C * (fat_i * weight_i_j) * (fat_i * weight_i_j - 2 * weight_i_j)
            bqm.add_variable(q[i][j], error_term)
            
            for k in range(j+1, num_bits_per_ingredient):
                weight_i_k = get_weight(i, k)
                error_term = 2 * C * (fat_i * weight_i_j) * (fat_i * weight_i_k)
                bqm.add_interaction(q[i][j], q[i][k], error_term)
                
            for m in range(i+1, num_ingredients):
                fat_m = ingredient_nutrition_per_g[ingredient_keys[m]]['fat']
                for n in range(num_bits_per_ingredient):
                    weight_m_n = get_weight(m, n)
                    error_term = 2 * C * (fat_i * weight_i_j) * (fat_m * weight_m_n)
                    bqm.add_interaction(q[i][j], q[m][n], error_term)
    
    for i in range(num_ingredients):
        for j in range(num_bits_per_ingredient):
            carb_i = ingredient_nutrition_per_g[ingredient_keys[i]]['carbs']
            weight_i_j = get_weight(i, j)
            error_term = D * (carb_i * weight_i_j) * (carb_i * weight_i_j - 2 * weight_i_j)
            bqm.add_variable(q[i][j], error_term)
            
            for k in range(j+1, num_bits_per_ingredient):
                weight_i_k = get_weight(i, k)
                error_term = 2 * D * (carb_i * weight_i_j) * (carb_i * weight_i_k)
                bqm.add_interaction(q[i][j], q[i][k], error_term)
                
            for m in range(i+1, num_ingredients):
                carb_m = ingredient_nutrition_per_g[ingredient_keys[m]]['carbs']
                for n in range(num_bits_per_ingredient):
                    weight_m_n = get_weight(m, n)
                    error_term = 2 * D * (carb_i * weight_i_j) * (carb_m * weight_m_n)
                    bqm.add_interaction(q[i][j], q[m][n], error_term)
    
    sampler = SASampler()
    sampleset = sampler.sample(bqm, num_reads=100)
    
    sample = sampleset.first.sample
    
    proportions = {}
    for i in range(num_ingredients):
        proportion = 0
        for j in range(num_bits_per_ingredient):
            if sample[q[i][j]] == 1:
                proportion += get_weight(i, j)
        proportions[ingredient_nutrition_per_g[f'ingredient{i+1}']['name']] = proportion * 100
    
    total = sum(proportions.values())
    if total > 0:
        for ingredient in proportions:
            proportions[ingredient] = (proportions[ingredient] / total) * 100
    
    calculated_nutrition = {
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0,
        'salt': 0
    }
    
    for i, ingredient_name in enumerate([ingredient_nutrition_per_g[f'ingredient{i+1}']['name'] for i in range(num_ingredients)]):
        proportion = proportions[ingredient_name] / 100
        for nutrient in ['calories', 'protein', 'fat', 'carbs', 'salt']:
            value = ingredient_nutrition_per_g[f'ingredient{i+1}'][nutrient]
            if nutrient == 'calories':
                value *= target_calories_g
            elif nutrient == 'protein':
                value *= target_protein_g
            elif nutrient == 'fat':
                value *= target_fat_g
            elif nutrient == 'carbs':
                value *= target_carbs_g
            
            calculated_nutrition[nutrient] += value * proportion
    
    result = {
        'proportions': proportions,
        'calculated_nutrition': {
            'per_gram': calculated_nutrition,
            'total': {
                nutrient: value * total_weight for nutrient, value in calculated_nutrition.items()
            }
        }
    }
    
    return result
