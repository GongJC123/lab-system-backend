from django.views.generic import View
from goods.models import Goods

# 此文件是未安装rest_framework的测试页，可以删除
class GoodsListView(View):
    def get(self,request):
        #通过django的view实现商品列表页
        json_list = []
        #获取所有商品
        goods = Goods.objects.all()
        # for good in goods:
        #     json_dict = {}
        #     #获取商品的每个字段，键值对形式
        #     json_dict['name'] = good.name
        #     json_dict['category'] = good.category.name
        #     json_dict['market_price'] = good.market_price
        #     json_list.append(json_dict)

        # 将整个model序列化
        from django.forms import model_to_dict  # 图片和日期不能序列化
        for good in goods:
            json_dict = model_to_dict(good)
            json_list.append(json_dict)

        # django的serializer虽然可以很简单实现序列化，但是有几个缺点
        # 字段序列化定死的，要想重组的话非常麻烦
        # images保存的是一个相对路径，我们还需要补全路径，而这些drf都可以帮助我们做到
        import json
        from django.core import serializers
        # 注意serializers的包，不是rest_framework的包
        json_data = serializers.serialize('json', goods)
        json_data = json.loads(json_data)

        from django.http import JsonResponse
        return JsonResponse(json_data, safe=False)