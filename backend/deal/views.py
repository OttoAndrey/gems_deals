import csv

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from deal.models import Users, Gem, Deal
from deal.serializers import DealSerializer, UsersSerializer, GemSerializer, FileUploadSerializer


class DealView(APIView):
    def get(self, request):
        most_spends_users = Users.objects.most_spends()[:5].prefetch_related('deals')

        # Формируем словарь,
        # где ключ-покупатель, значение-названия камней,
        # которые он покупал (без повторений).
        users_gems = {}
        for user in most_spends_users:
            user_gems = set(deal.item for deal in user.deals.select_related('item'))
            users_gems[user] = user_gems

        # Начинаем формировать список пользователей,
        # который вернем в ответ на запрос.
        users = []
        for user in most_spends_users:
            # Перебираем самых затратных покупателей еще раз
            # и убираем их словаря с камнями текущего покупателя.
            user_gems = users_gems.pop(user)

            # Создаём список со всеми камнями других пользователей.
            other_user_gems = []
            for gems in users_gems.values():
                other_user_gems.extend(gems)

            # Если камень, который покупал текущий пользователь,
            # будет среди камней других пользователей,
            # тогда добавляем его в ответ на запрос.
            cross_gems = []
            for user_gem in user_gems:
                if user_gem in other_user_gems:
                    cross_gems.append(user_gem.title)

            # Возвращаем пользователя обратно в словарь.
            users_gems[user] = user_gems
            users.append({'username': user.username,
                          'spent_money': user.total_sum,
                          'gems': cross_gems})
        return Response(users, status=status.HTTP_200_OK)

    def post(self, request):
        file_serializer = FileUploadSerializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        file = file_serializer.validated_data['deals']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        deals = []
        for row in reader:
            dict_row = dict(row)
            user_serializer = UsersSerializer(data=dict_row)
            user_serializer.is_valid(raise_exception=True)
            user, created = Users.objects.get_or_create(username=user_serializer.validated_data['username'])

            gem_serializer = GemSerializer(data=dict_row)
            gem_serializer.is_valid(raise_exception=True)
            gem, created = Gem.objects.get_or_create(title=gem_serializer.validated_data['title'])

            deal_serializer = DealSerializer(data=dict_row)
            deal_serializer.is_valid(raise_exception=True)

            deal = Deal(
                customer=user,
                item=gem,
                total=deal_serializer.validated_data['total'],
                quantity=deal_serializer.validated_data['quantity'],
                date=deal_serializer.validated_data['date'],
            )
            deals.append(deal)

        Deal.objects.bulk_create(deals)

        content = []
        for deal in deals:
            response_serializer = DealSerializer(deal)
            content.append(response_serializer.data)
        return Response(content, status=status.HTTP_201_CREATED)
