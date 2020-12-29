import csv

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from deal.models import Users, Gem, Deal


class DealView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DealView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        most_spents_users = Users.objects.annotate(total_sum=Sum('deals__total')).order_by('-total_sum')[:5]

        users_gems = {}
        for user in most_spents_users:
            user_gems = list(set(deal.item.title for deal in Deal.objects.filter(customer=user)))
            users_gems[user] = user_gems

        users = {}
        for user in most_spents_users:
            user_gems = users_gems.pop(user)

            without_current_user_all_gems = []
            for gems in users_gems.values():
                without_current_user_all_gems.extend(gems)

            answer_gems = []
            for user_gem in user_gems:
                if user_gem in without_current_user_all_gems:
                    answer_gems.append(user_gem)

            users_gems[user] = user_gems
            users[user.username] = {'spent_money': user.total_sum,
                                    'gems': answer_gems}
        return JsonResponse(users, status=200)

    def post(self, request, *args, **kwargs):
        file = request.FILES['deals_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        deals = []
        for row in reader:
            user, created = Users.objects.get_or_create(username=row['customer'])
            gem, created = Gem.objects.get_or_create(title=row['item'])
            deal = Deal(
                customer=user,
                item=gem,
                total=row['total'],
                quantity=row['quantity'],
                date=row['date']
            )
            deals.append(deal)
        Deal.objects.bulk_create(deals)
        return HttpResponse('Успешно перенес объекты из файла в БД!', status=201)
