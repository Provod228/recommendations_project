import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dot, Dense, Concatenate
from tensorflow.keras.optimizers import Adam
from django.db.models import Count, Avg
from .models import *


class RecommendationEngine:
    def __init__(self):
        self.content_similarity_matrix = None
        self.user_item_matrix = None
        self.deep_model = None
        self.content_features = None
        self.user_features = None

    def prepare_content_features(self):
        # Собираем фичи для контента
        contents = Content.objects.all().prefetch_related('creator', 'type_content', 'reasons_to_buy')

        content_data = []
        for content in contents:
            creators = " ".join([c.name for c in content.creator.all()])
            reasons = " ".join([r.summery for r in content.reasons_to_buy.all()])

            content_data.append({
                'id': content.id,
                'title': content.title,
                'summary': content.summery,
                'type': content.type_content.title_type,
                'creators': creators,
                'reasons': reasons,
                'evaluation': content.evaluation
            })

        df = pd.DataFrame(content_data)

        # Создаем текстовые фичи
        df['content_features'] = df['title'] + " " + df['summary'] + " " + df['type'] + " " + df['creators'] + " " + df[
            'reasons']

        # Векторизуем текст
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['content_features'])

        # Матрица схожести контента
        self.content_similarity_matrix = cosine_similarity(tfidf_matrix)
        self.content_features = df.set_index('id')['evaluation'].to_dict()

        return df

    def prepare_user_item_matrix(self):
        # Собираем данные о взаимодействиях пользователей
        interactions = UserInteraction.objects.select_related('user', 'content')

        data = []
        for interaction in interactions:
            data.append({
                'user_id': interaction.user.id,
                'content_id': interaction.content.id,
                'rating': interaction.rating if interaction.rating else 0,
                'viewed': int(interaction.viewed),
                'liked': int(interaction.liked),
                'time_spent': interaction.time_spent
            })

        if not data:
            return None

        df = pd.DataFrame(data)

        # Создаем взвешенный рейтинг
        df['weighted_rating'] = (
                df['rating'] * 0.6 +
                df['liked'] * 0.3 +
                df['viewed'] * 0.1 +
                np.log1p(df['time_spent']) * 0.2
        )

        # Создаем user-item матрицу
        self.user_item_matrix = df.pivot_table(
            index='user_id',
            columns='content_id',
            values='weighted_rating',
            fill_value=0
        )

        return df

    def build_deep_learning_model(self, num_users, num_contents, embedding_size=50):
        # Входные слои
        user_input = Input(shape=(1,), name='user_input')
        content_input = Input(shape=(1,), name='content_input')

        # Эмбеддинги
        user_embedding = Embedding(num_users, embedding_size, name='user_embedding')(user_input)
        content_embedding = Embedding(num_contents, embedding_size, name='content_embedding')(content_input)

        # Вытягиваем эмбеддинги
        user_vec = Flatten()(user_embedding)
        content_vec = Flatten()(content_embedding)

        # Конкатенируем и добавляем полносвязные слои
        concat = Concatenate()([user_vec, content_vec])
        dense1 = Dense(128, activation='relu')(concat)
        dense2 = Dense(64, activation='relu')(dense1)
        output = Dense(1, activation='sigmoid')(dense2)

        # Собираем модель
        self.deep_model = Model(inputs=[user_input, content_input], outputs=output)
        self.deep_model.compile(optimizer=Adam(0.001), loss='mse')

        return self.deep_model

    def train_deep_model(self, epochs=10, batch_size=64):
        if not self.user_item_matrix or not self.content_features:
            raise ValueError("Prepare user-item matrix and content features first")

        # Подготовка данных
        user_ids = []
        content_ids = []
        ratings = []

        for user_idx, user_id in enumerate(self.user_item_matrix.index):
            for content_idx, content_id in enumerate(self.user_item_matrix.columns):
                rating = self.user_item_matrix.iloc[user_idx, content_idx]
                if rating > 0:
                    user_ids.append(user_idx)
                    content_ids.append(content_idx)
                    ratings.append(rating)

        if not user_ids:
            raise ValueError("No interaction data available for training")

        # Нормализация рейтингов
        ratings = np.array(ratings) / 10.0

        # Преобразуем в numpy массивы
        user_ids = np.array(user_ids)
        content_ids = np.array(content_ids)

        # Обучаем модель
        self.build_deep_learning_model(
            num_users=len(self.user_item_matrix.index),
            num_contents=len(self.user_item_matrix.columns)
        )

        history = self.deep_model.fit(
            x=[user_ids, content_ids],
            y=ratings,
            batch_size=batch_size,
            epochs=epochs,
            validation_split=0.2,
            verbose=1
        )

        return history

    def recommend_for_user(self, user_id, top_n=5):
        if not self.deep_model or not self.user_item_matrix or not self.content_similarity_matrix:
            raise ValueError("Models not trained or data not prepared")

        # Получаем индекс пользователя
        try:
            user_idx = list(self.user_item_matrix.index).index(user_id)
        except ValueError:
            # Новый пользователь - возвращаем популярный контент
            return self.get_popular_content(top_n)

        # Получаем все content_id
        all_content_ids = list(self.user_item_matrix.columns)

        # Предсказываем рейтинги для всех контентов
        user_indices = np.array([user_idx] * len(all_content_ids))
        content_indices = np.array([list(self.user_item_matrix.columns).index(cid) for cid in all_content_ids])

        predicted_ratings = self.deep_model.predict([user_indices, content_indices]).flatten()

        # Сортируем по убыванию рейтинга
        recommended_indices = np.argsort(predicted_ratings)[::-1][:top_n]
        recommended_content_ids = [all_content_ids[i] for i in recommended_indices]

        # Получаем контент
        recommended_content = Content.objects.filter(id__in=recommended_content_ids)

        return recommended_content

    def get_popular_content(self, top_n=5):
        # Возвращаем популярный контент (для новых пользователей)
        popular_content = Content.objects.annotate(
            num_likes=Count('user__content_like'),
            avg_rating=Avg('evaluation')
        ).order_by('-num_likes', '-avg_rating')[:top_n]

        return popular_content

    def get_similar_content(self, content_id, top_n=5):
        if not self.content_similarity_matrix:
            raise ValueError("Content similarity matrix not prepared")

        # Получаем индекс контента
        content_ids = list(self.content_features.keys())
        try:
            content_idx = content_ids.index(content_id)
        except ValueError:
            return []

        # Получаем схожесть
        sim_scores = list(enumerate(self.content_similarity_matrix[content_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Берем топ-N
        sim_scores = sim_scores[1:top_n + 1]  # Исключаем сам контент
        similar_content_ids = [content_ids[i[0]] for i in sim_scores]

        # Получаем контент
        similar_content = Content.objects.filter(id__in=similar_content_ids)

        return similar_content