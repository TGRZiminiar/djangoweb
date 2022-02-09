

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart,CartItem
from store.models import Product, Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request): #private function เพื่อหาคุกกี้ว่าตัวนั่นเป็นตัวไหน
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart 


def add_cart(request,product_id):
    product = Product.objects.get(id=product_id) #เพื่อรู้ว่าเป้นโพดักตัวไหน
    product_variation = []
    if request.method == 'POST': #condition รับค่าสีกับsize
        for item in request.POST:
            key = item
            value = request.POST[key] #ต้องตรงกับ variation_value ใน model เลยต้องสร้างอีกเงื่อนไข

            try:
                variation = Variation.objects.get(product = product ,variation_category__iexact=key , variation_value__iexact = value)#เช็คว่า key,value ตรงกับ variation category ไหม
                #iexact ไม่สนใจว่าจะเป็นตัวใหญ่หรือตัวเล้ก
                product_variation.append(variation)

            except:
                pass

    try:
        cart = Cart.objects.get(cart_id = _cart_id(request)) # เรียกใช้คุกกี้เพื่อให้รู้ว่าcart id ของอะไรโดนใช้ session
        
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product = product , cart=cart) #กรองว่ามีข้อมูลที่เป็นสินค้าอยู่ในcartไหม
    if is_cart_item_exists: #ถ้ามีสินค้าอยู่ในcart
        cart_item = CartItem.objects.filter(product=product, cart=cart) #return cartitem object
        #existing variation --> database
        #current variation --> product_variation
        #itemid --> database
        existing_var_list = [] #list รอรับสินค้าที่เคยมีอยู่แล้ว
        id = [] #list ว่างรอรับค่า id สินค้า
        for item in cart_item: #วนลูปสินค้าในcart
            existing_variation = item.variation.all() #เก็บสินค้าทั้งหมดไว้ในตัวแปลนึง
            existing_var_list.append(list(existing_variation)) #ใส่ลงไปใน list ที่สร้างรอไว้
            id.append(item.id) #เก็บไอดีสินค้าไว้ในตัวแปรlist ที่สร้าไว้

        print(existing_var_list)
        
        if product_variation in existing_var_list: #ถ้าสีกับไซส์ตรงกับสินค้าที่มีอยู่แล้ว
            #increase quantity
            index = existing_var_list.index(product_variation) #เก็บไว้ในตัวแปรนึงโดยใช้ index
            item_id = id[index] 
            item = CartItem.objects.get(product = product , id =item_id)
            item.quantity +=1
            item.save()

        else: # create newone
            item = CartItem.objects.create(product=product ,cart=cart,quantity = 1)
            if len(product_variation) > 0:
                item.variation.clear()    
                item.variation.add(*product_variation) #ใส่ดอกจันทร์เพื่อยัดค่าสีกับไซส์เข้าไป2ค่า
            #cart_item.quantity +=1 
            item.save()
    
    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1, #quality = จำนวนสินค้าที่จะซื้อ ตั้งชื่อผิดแต่ขกแก้
            cart = cart,
            
        )
        if len(product_variation) > 0:
            cart_item.variation.clear()
            cart_item.variation.add(*product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product,id = product_id)
    try:
            
        cart_item = CartItem.objects.get(product = product , cart = cart ,id = cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
        cart = Cart.objects.get(cart_id = _cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product = product , cart = cart , id = cart_item_id)
        cart_item.delete()
        return redirect('cart')


def cart(request, total=0,quantity = 0,cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = float((0.07*total))
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {  #context มีเพื่อที่จะเก็บค่าทุกอย่างเป็น dict ละส่งต่อให้หน้า cart
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total, 
    }
    return render(request,'store/cart.html',context)



