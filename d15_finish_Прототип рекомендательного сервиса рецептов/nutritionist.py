import recipes
import pandas as pd

ingr = pd.read_csv('data/ingredients.csv')

must_nutrients = ['Protein', 'Total lipid (fat)', 'Calcium, Ca', 'Iron, Fe', \
                  'Magnesium, Mg', 'Phosphorus, P', 'Potassium, K', 'Sodium, Na', \
                  'Zinc, Zn', 'Copper, Cu', 'Selenium, Se', 'Vitamin A, RAE',  \
                  'Vitamin E (alpha-tocopherol)', 'Vitamin D (D2 + D3)',     \
                  'Vitamin C, total ascorbic acid', 'Thiamin', 'Riboflavin',   \
                  'Niacin', 'Vitamin B-6', 'Vitamin B-12', 'Choline, total',     \
                  'Vitamin K (phylloquinone)', 'Cholesterol', 'Fatty acids, total saturated', \
                  'Pantothenic acid', 'Manganese, Mn', 'Biotin']
n = 6


while True:
    list_of_ingredient = input('Введите продукты, для приготовления блюда, через запяую (на английском):').split(',')
    list_of_ingredients = []
    i_not = []
    for i in list_of_ingredient:
        if i.strip() not in list(ingr['0']):
            i_not.append(i)
            continue

    if len(i_not) > 0:
       print('Сочетание ваши продукты {} мы не нашли или нет ",". Попробуйте еще раз.'.format(i_not))
       break

    if len(i_not) == 0:
        for j in list_of_ingredient:
            if j not in i_not:
                list_of_ingredients.append(j.strip())

    if len(list_of_ingredients) >= 1:
        forecast_1 = recipes.Forecast(list_of_ingredients).predict_rating_category()
        print(forecast_1, '\n')
        forecast_2 = recipes.NutritionFacts(list_of_ingredients).filter(must_nutrients, n)
        forecast_2
        forecast_3 = recipes.SimilarRecipes(list_of_ingredients).top_similar(3)
        forecast_3
        break
