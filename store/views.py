from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.form import ReviewForm
from .models import Product, ReviewRating
from category.models import category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger , Paginator
from django.db.models import Q
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.
def store(request,category_slug = None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(category ,slug = category_slug)
        products = Product.objects.filter(category=categories, is_avaliable=True)
        paginator = Paginator(products, 1) #1 หน้าจะให้โชว์สินค้ากี่อัน
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.all().filter(is_avaliable = True).order_by('id')
        paginator = Paginator(products, 6) #1 หน้าจะให้โชว์สินค้ากี่อัน
        page = request.GET.get('page')
        paged_products = paginator.get_page(page) #เก็ทหน้าที่มีproduct 6 อัน
        product_count = products.count()

    context = {
        'products':paged_products,
        'product_count':product_count,

        
    }
    return render(request, 'store/store.html',context)



def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)  #__ คือ get access to the slug model
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists()

    except Exception as e: #บรรทัดนี้หมายความว่าถ้ามีข้อผิดพลาดก้ให้ทำแบบเดิม
        raise e 
    
    if request.user.is_authenticated:
        try: #เช็คว่าเขาซื้อสินค้าชิ้นนี้หรือยัง
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id = single_product.id).exists() #ที่ใช้singleproductได้เพราะข้างบนมีsingleอยุ่แล้ว

        except OrderProduct.DoesNotExist:
            orderproduct = None

    else:
        orderproduct = None
    #get review 
    reviews = ReviewRating.objects.filter(product_id = single_product.id,status = True)



    context = {
        'single_product':   single_product,
        'in_cart'       :   in_cart,
        'orderproduct'  :   orderproduct,
        'reviews'       :   reviews,
    }
    return render(request, 'store/product_detail.html',context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword: #ถ้า keyword มีค่าที่รับมา
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q (product_name__icontains = keyword)) #เอา keyword ไปเทียบกับคำใน description ถ้าเจอจะดึงสินค้าไปแสดงที่หน้า
            product_count = products.count()
        else: #icontains แปลว่าทั้งหมดของอะไรที่อยู่ข้างหน้า
            pass    
    context = {
        'products':products,
        'product_count':product_count, 
    }


    return render(request, 'store/store.html',context)



def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') #เก็บหน้า url หน้าที่เรากำลังอยู่อยู่มาในตัวแปร url
    if request.method =="POST":
        try: #กรณีที่เคยเขียนแล้ว updated form
            reviews = ReviewRating.objects.get(user__id = request.user.id,product__id = product_id)
            #ที่ใช้ __ เพราะว่าต้องการจะอิงถึง user ใน class submit_review
            # product__id = อิงไปถึงproduct ใน class submit_review _id คือเข้าถึงid
            
            form = ReviewForm(request.POST,instance=reviews) 
            #ใส่ requset.POST เพราะจะมีข้อมูลทั้งหมดเช่น ดาว รีวิวต่างๆ
            #ต้องใส่ instance = reviews เพื่อที่จะตรวจสอบว่า user คนนี้ที่มี id เป้นอันนี้เคยเขียนที่สินค้านี้แล้วหรือยังถ้าเคยแล้วให้ update ถ้าไม่เคยจะสร้างอันใหม่
            form.save()
            messages.success(request,'Thank you for your review!Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist: #กรณีไม่เคยเขียนต้องสร้างฟอมใหม่
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject    =   form.cleaned_data['subject']
                data.rating     =   form.cleaned_data['rating']
                data.review     =   form.cleaned_data['review']
                data.ip         =   request.META.get('REMOTE_ADDR') #เก็บค่า IP address = REMOTE_ADDR
                data.product_id =   product_id
                data.user_id    =   request.user.id
                data.save()
                messages.success(request,'Your review has been submitted!')
                return redirect(url)

