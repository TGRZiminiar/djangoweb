from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from carts.models import Cart, CartItem
from .form import OrderForm
from .models import Order, OrderProduct,Payment
import datetime , json
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Create your views here.
def place_order(request,total = 0,quantity=0,):
    #ถ้าของในcart น้อยกว่าหรือเท่ากับ 0 ให้redirectไปที่ store
    current_user = request.user
    cart_items   = CartItem.objects.filter(user = current_user) #รับค่าสินค้าในcart
    cart_count  = cart_items.count() #นับจำนวนสินค้าใน cart
    if cart_count <= 0: #ถ้าไม่มีสินค้า
        return redirect('store')

    grand_total = 0
    tax         = 0
    
    for cart_item in cart_items:
        total    += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = float((0.07*total))
    tax = float(('%.3f' %(tax)))
    grand_total = total + tax


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid(): #ถ้า request post ส่งเข้ามาถูกต้อง จะให้เก็บข้อมูลไว้ในตาราง Ordertable
            data = Order() #เรียก class Order เข้ามา
            data.user           = current_user
            data.first_name     = form.cleaned_data['first_name'] #วิธีจะเอาค่าvalueจาก request.post
            data.last_name      = form.cleaned_data['last_name']
            data.phone          = form.cleaned_data['phone']
            data.email          = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country        = form.cleaned_data['country']
            data.state          = form.cleaned_data['state']
            data.city           = form.cleaned_data['city']
            data.order_note     = form.cleaned_data['order_note']
            data.order_total    = grand_total
            data.tax            = tax
            data.ip             = request.META.get('REMOTE_ADDR') #วิธีการเก็บค่า user ip
            data.save()

            #สร้าง order number
            yr = int(datetime.date.today().strftime('%Y')) #เก็บวันที่วันนี้ และเก็บค่าปี %Y = ปี
            dt = int(datetime.date.today().strftime('%d')) #เก็บค่าวัน %d = วัน
            mt = int(datetime.date.today().strftime('%m')) 
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id) #เพราะเซฟ data ไปแล้วที่ยรรทัด 44 เลยเรียกใช้ id ได้
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user = current_user , is_ordered = False, order_number = order_number)

            context = {
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }

            return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')

def payments(request):
    body = json.loads(request.body) #เรียกข้อมูลจากหน้า payments.html 
    order = Order.objects.get(user = request.user, is_order = False , order_number = body['orderID'])
    # เอาค่าที่ได้จาก paypal เก้บใน database 
    #เก็บเข้าdatabase ได้เพราะเรียก class Order มาแล้ว
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
 # <------ จบการส่งข้อมูลของ Paypal เข้า database table payments ------>


    #ส่งข้อมูลในcart ไปที่ table order product   
    cart_items = CartItem.objects.filter(user = request.user,)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment #payment ยรรทัด 77
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        #orderproduct.variations = item.variations แบบนี้ไม่ได้เพราะใน Model ใส่่เป้น manytomanyfield
        #จะเอาค่า variation จาก cartitem โดยใช้ id
        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()
        orderproduct = orderproduct.objects.get(id = orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        # ลดquantity ของสินค้าลงหลังจากจ่ายเงิน
        product = Product.objects.get(id = item.product_id) #ใช้ไอดีสินค้าว่าเป็นสินค้าไหน
        product.stock -= item.quantity #เอาของในstock ลบกับ จำนวนที่ซื้อใน cart
        product.save()


    #ลบสินค้าใน cart
    CartItem.objects.filter(user = request.user).delete() #ใน user ตอนนี้เป็นตัวเก็บของไปแล้วเพราะเราเก็บจาก session id เลยต้องใช้ user


    #send email ว่าเสร้จสิ้นแล้ว
    user = request.user
    email_subject = 'Thankyou for your order!'
    message = render_to_string('orders/order_recieved_email.html',{ #ส่ง templates ที่ทำไว้ไปในหน้าemail
        'user'  : user, #user object เพราะต้องใช้ชื่อของuser.first_name เลยต้องส่งเข้า user เข้ามา
        'order' : order
    }) 
    to_email   = user.email #เอาคำที่จะส่งเก็บไว้ในตัวแร
    send_email = EmailMessage(email_subject, message, to=[to_email]) #เอาของที่จะส่งมาเก็บไว้ในตัวแปรทั้งหมด
    send_email.send() #ส่งอีเมล์


    #send order number and transection id back to sendData method to jsonresponse
    data = {
        'order_number':order.order_number,
        'transID' : payment.payment_id #เอามาจากบรรทัด81

    }


    return JsonResponse(data) #จะส่งกลับไปที่ที่มันมาก็คือที่ฟังก์ชัน SendData ใน payment.html



def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    subtotal = 0
    for i in order_product:
        subtotal += i.product_price * i.quantity
    
    try:
        order = Order.objects.get(order_number = order_number,transID = transID)
        order_product = Product.objects.filter(order_id = order.id)
        payment = Payment.objects.get(payment_id = transID)
       
        context = {
            'order'         :order,
            'order_product' :order_product,
            'order_number'  :order.order_number,
            'transID'       :payment.payment_id,
            'created_at'    :order.created_at,
            'status'        :order.status,
            'subtotal'      :subtotal,
        }
        return render(request,'orders/order_complete.html',context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
        