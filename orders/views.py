from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order


def payments(request): #ระบบจ่ายเงิน
    return render(request, 'orders/qrcode.html')


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (7 * total)/100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city'] 
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


from django.http import HttpResponse
from PIL import Image
import libscrc
import qrcode

def calculate_crc(code):
    crc = libscrc.ccitt_false(str.encode(code))
    crc = str(hex(crc))
    crc = crc[2:].upper()
    return crc.rjust(4, '0')

# def gen_code(mobile="", amount=1.23):
#     code="00020101021153037645802TH29370016A000000677010111"
#     if mobile:
#         tag,value = 1,"0066"+mobile[1:]
#         seller='{:02d}{:02d}{}'.format(tag,len(value), value)
#     else:
#         raise Exception("Error: gen_code() does not get seller mandatory details")
#     code+=seller
#     tag,value = 54, '{:.2f}'.format(amount)
#     code+='{:02d}{:02d}{}'.format(tag,len(value), value)
#     code+='6304'
#     code+=calculate_crc(code)
#     return code

# def get_qr(request,mobile="",amount=""):
#     message="mobile: %s, amount: %s"%(mobile,amount)
#     print(message)
#     print(f'{mobile} : {amount}')
#     code=gen_code(mobile=mobile, amount=float(amount))#scb
#     print(code)
#     img = qrcode.make(code,box_size=4)
#     response = HttpResponse(content_type='image/png')
#     img.save(response, "PNG")
#     return response

def get_qr(request,mobile="", amount=""):
    code="00020101021153037645802TH29370016A000000677010111"
    if mobile:
        tag,value = 1,"0066"+mobile[1:]
        seller = f"{tag:02d}{len(value):02d}{value}"
        print(seller)
    else:
        raise Exception("Error: gen_code() does not get seller mandatory details")
    code+=seller
    tag,value = 54, f'{float(amount):.2f}'
    code+=f"{tag:02d}{len(value):02d}{value}"
    code+='6304'
    crc = libscrc.ccitt_false(str.encode(code))
    crc = str(hex(crc))
    crc = crc[2:].upper()
    code+=crc.rjust(4, '0')
    message="mobile: %s, amount: %s"%(mobile,amount)
    print(code)
    img = qrcode.make(code,box_size=4)
    response = HttpResponse(content_type='image/png')
    response['Content-Type'] = 'text/html; charset=utf-8'
    img.save(response, "PNG")
    return response    

# def get_qr(request,mobile="",nid="",amount=""):
#     message="mobile: %s, nid: %s, amount: %s"%(mobile,nid,amount)
#     print( message )
#     code=gen_code(mobile=mobile, amount=float(amount))#scb
#     print(code)
#     img = qrcode.make(code,box_size=4)
#     response = HttpResponse(content_type='image/png')
#     img.save(response, "PNG")
#     return response

def qrcode(request, total=0, quantity=0):
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (7 * total)/100
    grand_total = total + tax   
    context={
        "mobile":"0969319333", #seller's mobile
        "amount": grand_total
    }
    return render(request, 'orders/qrcode.html', context)
