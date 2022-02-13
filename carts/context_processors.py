import re
from .models import Cart,CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))   #เรียกใช้ฟังก์ชันจาก view cart เพื่อเอาค่า session id
            if request.user.is_authenticated: #ถ้า user login
                cart_items = CartItem.objects.all().filter(user=request.user) # ไปเอาค่าจาก cartitem จากuser มาก็คือจะมีตัวนึงที่เก้บ session user ว่ามีสินค้าอะไรบ้างที่เคยกดไว้ตอนไม่login

            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1]) #เอาสินค่าในcart มาเก้บในตัวแปร
            
            for cart_item in cart_items:
                cart_count += cart_item.quantity #เก็บค่าจำนวนสินค้า
        except Cart.DoesNotExist: #ถ้าไม่มี
            cart_count = 0 
    return dict(cart_count = cart_count)


