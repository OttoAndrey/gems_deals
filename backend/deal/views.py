import csv

from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from deal.models import Users, Gem, Deal
from deal.serializers import DealSerializer, UsersSerializer, GemSerializer, FileUploadSerializer


class DealView(APIView):
    def get(self, request):
        most_spends_users = Users.objects.annotate(total_sum=Sum('deals__total')).order_by('-total_sum')[:5]

        users_gems = {}
        for user in most_spends_users:
            user_gems = list(set(deal.item.title for deal in Deal.objects.filter(customer=user)))
            users_gems[user] = user_gems

        users = []
        for user in most_spends_users:
            user_gems = users_gems.pop(user)

            without_current_user_all_gems = []
            for gems in users_gems.values():
                without_current_user_all_gems.extend(gems)

            answer_gems = []
            for user_gem in user_gems:
                if user_gem in without_current_user_all_gems:
                    answer_gems.append(user_gem)

            users_gems[user] = user_gems
            users.append({'username': user.username,
                          'spent_money': user.total_sum,
                          'gems': answer_gems})
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
