import pandas as pd
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.simplefilter(action='ignore')


class Forecast:
    """ 
    Предсказание рейтинга блюда или его класса
    """
    def __init__(self, list_of_ingredients):
        """
        Добавьте сюда любые поля и строчки кода, которые вам покажутся нужными.
        """
        self.list_of_ingredients = list_of_ingredients
        self.ingredient = pd.read_csv('data/recipes.csv')
        self.ingredient = self.ingredient.drop(columns=['title', 'rating', 'link_recipe', 'rating_numbers'])


    def preprocess(self):
        """
        Этот метод преобразует список ингредиентов в структуры данных, 
        которые используются в алгоритмах машинного обучения, чтобы сделать предсказание.
        """

        vector = pd.DataFrame(np.zeros(self.ingredient.shape), columns=self.ingredient.columns)
        if set(self.list_of_ingredients).issubset(self.ingredient.columns):
            vector[self.list_of_ingredients] = 1
        return vector

    def predict_rating_category(self):
        """
        Этот метод возращает рейтинговую категорию для списка ингредиентов, используя классификационную модель, 
        которая была обучена заранее. Помимо самого рейтинга, метод возвращает также и текст, 
        который дает интерпретацию этой категории и дает рекомендации, как в примере выше.
        """
        model = joblib.load("data/best_RandomForestClassifier.pkl")

        print('I. НАШ ПРОГНОЗ:\n')

        y_pred = model.predict(self.preprocess())

        seal = {'bad': 'Невкусное. Хотели предупредить. А может просто не пробовали.',
                'so-so': 'Нормальное. Можете приготовить блюдо из данного набора продуктов и возможно оно вам понравиться. Или можно пискать другие сочетания.',
                'great': 'Вкусное. Можете приготовить блюдо из данного набора продуктов.'}

        rating_cat = y_pred[0]
        text = seal[rating_cat]

        return rating_cat, text


class NutritionFacts:
    """
    Выдает информацию о пищевой ценности ингредиентов.
    """
    def __init__(self, list_of_ingredients):
        """
        Добавьте сюда любые поля и строчки кода, которые вам покажутся нужными.
        """
        self.nutrients = pd.read_csv('data/nutritional_value.csv')
        self.list_of_ingredients = list_of_ingredients

    def retrieve(self):
        """
        Этот метод получает всю имеющуюся информацию о пищевой ценности из файла с заранее собранной информацией по заданным ингредиентам. 
        Он возвращает ее в том виде, который вам кажется наиболее удобным и подходящим.
        """

        facts = pd.DataFrame(columns=self.nutrients.columns)

        for i in self.list_of_ingredients:
            i_ingredient = self.nutrients.loc[self.nutrients.ingredient == i]
            facts = pd.concat([facts, i_ingredient], sort=False, axis=0, ignore_index=True)
        return facts

    def filter(self, must_nutrients, n):
        """
        Этот метод отбирает из всей информации о пищевой ценности только те нутриенты, которые были заданы в must_nutrients (пример в PDF-файле ниже), 
        а также топ-n нутриентов с наибольшим значением дневной нормы потребления для заданного ингредиента. 
        Он возвращает текст, отформатированный как в примере выше.
        """
        facts = self.retrieve()

        print('II. ПИЩЕВАЯ ЦЕННОСТЬ:')

        for i in self.list_of_ingredients:
            sort_ingredient = facts.loc[facts['ingredient'] == i].sort_values('%_daily_norm')
            print('\n', i.title(), ':')

            for j in range(len(must_nutrients)):
                if j < n:
                    if must_nutrients[j] in sort_ingredient['nutrient'].to_list():
                        daily_norm = sort_ingredient.loc[sort_ingredient['nutrient'] == must_nutrients[j]]['%_daily_norm']
                        print(f'{must_nutrients[j]} - {float(daily_norm):.2f} % of Daily Value')
                    else:
                        print(f'Данных по {must_nutrients[j]} для {i} не найденo')
                else:
                    break




class SimilarRecipes:
    """
    Рекомендация похожих рецептов с дополнительной информацией
    """
    def __init__(self, list_of_ingredients):
        """
        Добавьте сюда любые поля и строчки кода, которые вам покажутся нужными.
        """
        self.list_of_ingredients = list_of_ingredients
        self.recipes = pd.read_csv('data/recipes.csv')
        self.ingredient = self.recipes.drop(columns=['title', 'rating', 'link_recipe', 'rating_numbers'])


    def find_all(self):
        """
        Этот метод возвращает список индексов рецептов, которые содержат заданный список ингредиентов. 
        Если нет ни одного рецепта, содержащего все эти ингредиенты, то сделайте обработку ошибки, чтобы программа не ломалась.
        """

        if set(self.list_of_ingredients).issubset(self.ingredient.columns):
            sample = self.ingredient[self.list_of_ingredients].sum(axis=1) == len(self.list_of_ingredients)
            return self.ingredient.loc[sample].index.to_list()
        else:
            return []

    
    def top_similar(self, n):
        """
        Этот метод возвращает текст, форматированный как в примере выше: с заголовком, рейтингом и URL. 
        Чтобы это сделать, он вначале находит топ-n наиболее похожих рецептов с точки зрения количества дополнительных ингредиентов, 
        которые потребуются в этих рецептах. Наиболее похожим будет тот, в котором не требуется никаких других ингредиентов. 
        Далее идет тот, у которого появляется 1 доп. ингредиент. Далее – 2. 
        Если рецепт нуждается в более, чем 5 доп. ингредиентах, то такой рецепт не выводится.
        """
        indexes = self.find_all()

        print(f'\nIII. ТОП-{n} ПОХОЖИХ РЕЦЕПТА:\n')

        if len(indexes) == 0:
            print('Похожих рецептов не нашлось. Попробуйте другие продукты.')
            return

        df_iloc = self.recipes.iloc[indexes]
        df_drop = df_iloc.drop(columns=['title', 'rating', 'link_recipe', 'rating_numbers'])
        df_drop['sum_ingredient'] = df_drop.sum(axis=1).to_list()
        df_concat = pd.concat([df_iloc, df_drop], sort=False, axis=1)

        df_sort = df_concat[['sum_ingredient', 'title', 'rating', 'link_recipe', 'rating_numbers']].sort_values(['sum_ingredient', 'rating_numbers'])  #ascending=[False, True])-сорт по убыванию
        df_sort.reset_index(inplace=True)

        df_final = df_sort[df_sort.sum_ingredient <= (len(self.list_of_ingredients) + 5)]

        for i in range(n):
            print('{}, рейтинг: {}, URL: {}'.format(df_final.at[i, 'title'], df_final.at[i, 'rating_numbers'], df_final.at[i, 'link_recipe']))
            if ((len(df_final) <= n) or (len(df_final) >= n)):
                return print("Ссылок с похожими рецептами больше не найдено")


