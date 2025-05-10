document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingMessage = document.getElementById('loadingMessage');
    const resultsSection = document.getElementById('resultsSection');
    const ingredientsInfo = document.getElementById('ingredientsInfo');
    const optimizationResults = document.getElementById('optimizationResults');
    const proportionsChart = document.getElementById('proportionsChart');
    const nutritionChart = document.getElementById('nutritionChart');
    
    // const API_ENDPOINT = '/analyze';
    
    const API_ENDPOINT = 'https://your-lambda-api-endpoint.amazonaws.com/analyze';
    
    analyzeBtn.addEventListener('click', async function() {
        const ingredientText = document.getElementById('ingredientText').value.trim();
        if (!ingredientText) {
            alert('原材料リストを入力してください');
            return;
        }
        
        const targetNutrition = {
            calories: parseFloat(document.getElementById('targetCalories').value),
            protein: parseFloat(document.getElementById('targetProtein').value),
            fat: parseFloat(document.getElementById('targetFat').value),
            carbs: parseFloat(document.getElementById('targetCarbs').value),
            salt: parseFloat(document.getElementById('targetSalt').value),
            total_amount: parseFloat(document.getElementById('totalAmount').value)
        };
        
        loadingMessage.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        
        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredient_text: ingredientText,
                    target_nutrition: targetNutrition
                })
            });
            
            if (!response.ok) {
                throw new Error('APIリクエストに失敗しました');
            }
            
            const data = await response.json();
            
            displayResults(data);
            
        } catch (error) {
            console.error('エラー:', error);
            alert('分析中にエラーが発生しました: ' + error.message);
        } finally {
            loadingMessage.classList.add('hidden');
        }
    });
    
    function displayResults(data) {
        let ingredientsHtml = '<table><tr><th>原材料</th><th>カテゴリ</th><th>カロリー</th><th>タンパク質</th><th>脂質</th><th>炭水化物</th><th>塩分</th></tr>';
        
        data.ingredients.ingredients.forEach(ingredient => {
            ingredientsHtml += `
                <tr>
                    <td>${ingredient.name}</td>
                    <td>${ingredient.category}</td>
                    <td>${ingredient.estimated_nutrition.calories} kcal</td>
                    <td>${ingredient.estimated_nutrition.protein} g</td>
                    <td>${ingredient.estimated_nutrition.fat} g</td>
                    <td>${ingredient.estimated_nutrition.carbs} g</td>
                    <td>${ingredient.estimated_nutrition.salt} g</td>
                </tr>
            `;
        });
        
        ingredientsHtml += '</table>';
        ingredientsInfo.innerHTML = ingredientsHtml;
        
        const result = data.optimization_result;
        const proportions = result.proportions;
        const calculatedNutrition = result.calculated_nutrition.total;
        
        let resultsHtml = '<h3>最適な配合比率</h3><table><tr><th>原材料</th><th>比率 (%)</th></tr>';
        
        Object.entries(proportions).forEach(([ingredient, proportion]) => {
            resultsHtml += `
                <tr>
                    <td>${ingredient}</td>
                    <td>${proportion.toFixed(2)}%</td>
                </tr>
            `;
        });
        
        resultsHtml += '</table><h3>計算された栄養成分値</h3><table><tr><th>栄養成分</th><th>値</th></tr>';
        
        resultsHtml += `
            <tr><td>カロリー</td><td>${calculatedNutrition.calories.toFixed(2)} kcal</td></tr>
            <tr><td>タンパク質</td><td>${calculatedNutrition.protein.toFixed(2)} g</td></tr>
            <tr><td>脂質</td><td>${calculatedNutrition.fat.toFixed(2)} g</td></tr>
            <tr><td>炭水化物</td><td>${calculatedNutrition.carbs.toFixed(2)} g</td></tr>
            <tr><td>食塩相当量</td><td>${calculatedNutrition.salt.toFixed(3)} g</td></tr>
        `;
        
        resultsHtml += '</table>';
        optimizationResults.innerHTML = resultsHtml;
        
        createProportionsChart(proportions);
        
        createNutritionChart(calculatedNutrition);
        
        resultsSection.classList.remove('hidden');
    }
    
    function createProportionsChart(proportions) {
        const canvas = document.createElement('canvas');
        proportionsChart.innerHTML = '';
        proportionsChart.appendChild(canvas);
        
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: Object.keys(proportions),
                datasets: [{
                    data: Object.values(proportions),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '原材料の配合比率'
                    }
                }
            }
        });
    }
    
    function createNutritionChart(nutrition) {
        const canvas = document.createElement('canvas');
        nutritionChart.innerHTML = '';
        nutritionChart.appendChild(canvas);
        
        const targetCalories = parseFloat(document.getElementById('targetCalories').value);
        const targetProtein = parseFloat(document.getElementById('targetProtein').value);
        const targetFat = parseFloat(document.getElementById('targetFat').value);
        const targetCarbs = parseFloat(document.getElementById('targetCarbs').value);
        const targetSalt = parseFloat(document.getElementById('targetSalt').value);
        const totalAmount = parseFloat(document.getElementById('totalAmount').value);
        
        const targetValues = {
            calories: targetCalories * totalAmount / 100,
            protein: targetProtein * totalAmount / 100,
            fat: targetFat * totalAmount / 100,
            carbs: targetCarbs * totalAmount / 100,
            salt: targetSalt * totalAmount / 100
        };
        
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['カロリー (kcal)', 'タンパク質 (g)', '脂質 (g)', '炭水化物 (g)', '食塩相当量 (g)'],
                datasets: [
                    {
                        label: '計算値',
                        data: [
                            nutrition.calories,
                            nutrition.protein,
                            nutrition.fat,
                            nutrition.carbs,
                            nutrition.salt
                        ],
                        backgroundColor: '#36A2EB'
                    },
                    {
                        label: '目標値',
                        data: [
                            targetValues.calories,
                            targetValues.protein,
                            targetValues.fat,
                            targetValues.carbs,
                            targetValues.salt
                        ],
                        backgroundColor: '#FF6384'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '栄養成分比較'
                    }
                }
            }
        });
    }
});
