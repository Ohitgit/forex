'''User log in & log out serializers'''
from rest_framework import serializers
from rest_framework_simplejwt.serializers import  TokenObtainPairSerializer
from django.contrib.auth.models import User
from .utils import Util
from django.core.mail import send_mail
from businessapp.models import *
from login.models import *
import boto3

class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"







class BlogseoSerializer(serializers.ModelSerializer):
    
    image_caption=serializers.ReadOnlyField(source='blog_id.image_caption')
    class Meta:
        model = Blog_Seo
        fields = "__all__"
        
        
class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'id')
    def to_representation(self, instance):
        rep = super(UserSerializer, self).to_representation(instance)
        
        rep['email'] = instance.email
        return rep
class LocationSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = location
        fields = ('id','city','city_status')
    



  
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = category
        fields = ('id','category_name','Category_Image','slug')
    

class LocationseoSerializer(serializers.ModelSerializer):
    # image= serializers.ImageField(source='category_id.og_image')
    class Meta:
        model = Location_Seo
        fields = ('id','meta_keyword','met_title','title','og_image','meta_description','location_description')
    

class Post_category_meta_valueSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = Post_category_meta_value
        fields = "__all__"
    def create(self, validated_data):
        cat_val =self.context['request'].data
        request = self.context['request']
        current_user = request.user
        validated_data['CRT_BY'] = current_user
        validated_data['MDF_BY'] = current_user
        category_id=cat_val.pop("category_id")
        print("===========",category_id)
        
        if cat_val['meta_keyword']:
            cat_val = Post_category_meta_value.objects.create(category_id_id=category_id,**validated_data)
            return cat_val
    def update(self, instance, validated_data):
        request = self.context["request"]
        current_user = request.user
        instance.MDF_BY = current_user
        instance.category_id_id=validated_data.get("category_id")
        instance.meta_keyword=validated_data.get("meta_keyword")
        instance.meta_title=validated_data.get("meta_title")
        instance.meta_category_Image=validated_data.get("meta_category_Image")
        instance.meta_tags=validated_data.get("meta_tags")
        instance.meta_description =validated_data.get("meta_description")
        instance.MDF_BY=current_user
        instance.save()
        return instance
        

class BusinessOwnerSerializers(serializers.ModelSerializer):
    class Meta:
        model=Business_Owner_detail
        fields="__all__"
    def create(self, validated_data):
        response =self.context['request'].data
        request = self.context['request']
        current_user = request.user
        validated_data['CRT_BY'] = current_user
        validated_data['MDF_BY'] = current_user
        if response['name']:
           response= Business_Owner_detail.objects.create(user=current_user,**validated_data)
        return response
    def update(self, instance, validated_data):
        request = self.context["request"]
        current_user = request.user
        instance.user = current_user
        # instance.name=validated_data.get("name")
        # instance.mobile_no=validated_data.get("mobile_no")
        # instance.email_optional=validated_data.get("email_optional")
        instance.Bank_Name=validated_data.get("Bank_Name")
        instance.Bank_Account_No=validated_data.get("Bank_Account_No")
        instance.Bank_Ifsc_Code =validated_data.get("Bank_Ifsc_Code")
        instance.save()
        return instance 


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = location
        fields = '__all__'


class Business_DetailsSerializers(serializers.ModelSerializer):
    city= serializers.ReadOnlyField(source='city.city',read_only=True)
    category  = serializers.CharField(source='category_id.category_name',read_only=True)
    
    mobile_no= serializers.ReadOnlyField(source='Business_Owner_detail.mobile_no',read_only=True)
    # category_description= serializers.ReadOnlyField(source='category_id.category_description',read_only=True)
    print('mobile_nos',mobile_no)
    # location=LocationSerializer
    class Meta:
        model=Business_Details
        fields=('id','business_logo','business_name','category','mobile_no','open_time','close_time','city','business_status')
    
class ServicesBusinessDetailsSerializers(serializers.ModelSerializer):
    city= serializers.ReadOnlyField(source='city.city',read_only=True)
    category  = serializers.CharField(source='category_id.category_name',read_only=True)
    
    mobile_no= serializers.ReadOnlyField(source='Business_Owner_detail.mobile_no',read_only=True)
    # category_description= serializers.ReadOnlyField(source='category_id.category_description',read_only=True)
    print('mobile_nos',mobile_no)
    # location=LocationSerializer
    class Meta:
        model=Business_Details
        fields=('id','business_logo','business_name','category','mobile_no','open_time','close_time','city','state','pincode','business_status')

class UpdateUserProfileSerializers(serializers.ModelSerializer):
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model=Business_Owner_detail
        fields=('name', 'mobile_no', 'email_optional','gender','birth','img','last_name')
    def create(self, validated_data):
        response =self.context['request'].data
        request = self.context['request']
        current_user = request.user
        validated_data['CRT_BY'] = current_user
        validated_data['MDF_BY'] = current_user
        if response['name']:
           response= Business_Owner_detail.objects.create(user=current_user,**validated_data)
        return response
    def update(self, instance, validated_data):
        request = self.context["request"]
        current_user = request.user
        print('--instanceokk',instance.user.last_name)
        user=User.objects.get(username=current_user)
        instances=Business_Owner_detail.objects.create(user=user)
        print('user',validated_data.get("user_last_name"))
        instances.name=validated_data.get("name")
        user.last_name=validated_data.get("last_name")
        instances.mobile_no=validated_data.get("mobile_no")
        instances.email_optional=validated_data.get("email_optional")

        instances.birth=validated_data.get("birth")
        instances.img=validated_data.get("img")

        instances.gender=validated_data.get("gender")
        # user.save()
        instances.save()
        return instances 


class UpdateRegisterProfileSerializers(serializers.ModelSerializer):
   
    usermobile= serializers.ReadOnlyField(source='user.username')
    class Meta:
        model=Register
        fields='__all__'
   
    def update(self, instance, validated_data):
        request = self.context["request"]
        current_user = request.user
        
        
        user1=Register.objects.get(user__username=current_user)
        
        if validated_data.get("img") == None:
            print('okkk555')
            instance.img=user1.img

        else:
            instance.img=validated_data.get("img")
        if validated_data.get("mobile_number") ==  None :
             instance.mobile_number=user1.mobile_number
        else:
             instance.mobile_number=validated_data.get("mobile_number")

        if validated_data.get("name")  ==  None :
              instance.name=user1.name
        else:
            instance.name=validated_data.get("name")
        

        if validated_data.get("email")  ==  None :
              instance.email=user1.email
        else:
            instance.email=validated_data.get("email")
    
        if  validated_data.get("birth") == None:
             instance.birth=user1.birth
        else:
             instance.birth=validated_data.get("birth")
        
        if  validated_data.get("gender") == None:
             instance.gender=user1.gender
        else:
             instance.gender=validated_data.get("gender")

        if  validated_data.get("last_name") == None:
             instance.last_name=user1.last_name
        else:
             instance.last_name=validated_data.get("last_name")
        
            
            
          
        instance.save()
        return instance


class BusinessGallerySerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = Business_Gallery
        fields = "__all__"
    def create(self, validated_data):
        request =self.context['request']
       
        businessdetails= request.data.get('business_details_id')  # Access the value without modifying the QueryDict
       
        # The rest of your code for creating the category goes here

        if request.data.get('description'):
            cat_val = Business_Gallery.objects.create(business_details_id_id=businessdetails,**validated_data)
            return cat_val
    def update(self, instance, validated_data):
    
        instance.Business_Details_id=validated_data.get("Business_Details")
        instance.image_gallery=validated_data.get("image_gallery")
        instance.description=validated_data.get("description")
        instance.save()
        return instance 
    



class SubcategorySerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = subcategory
        fields = "__all__"
    def create(self, validated_data):
        request =self.context['request']
       
        businessdetails= request.data.get('category_name') 

        if request.data.get('subcategory_name'):
            cat_val = subcategory.objects.create(category_name_id=businessdetails,**validated_data)
            return cat_val
        
    def update(self, instance, validated_data):
    
        instance.category_name_id=validated_data.get("category_name")
        instance.subcategory_name=validated_data.get("subcategory_name")
        instance.subcategory_image=validated_data.get("subcategory_image")
        instance.slug=validated_data.get("slug")
        instance.description=validated_data.get("description")
        instance.Business_id=validated_data.get("Business")
        instance.status=validated_data.get("status")
        instance.save()
        return instance 





class ServiceSerializers(serializers.ModelSerializer):
    # businessgallery = serializers.CharField(source='businessgalery.image_gallery')
    # businessname  = serializers.CharField(source='business_details_id.business_name')
    # category  = serializers.CharField(source='category_id.category_name')
    # address  = serializers.CharField(source='business_details_id.address')
    # # business_img  = serializers.CharField(source='business_details_id.address')
    # mapurl = serializers.CharField(source='business_details_id.map_url')
    # open_time = serializers.CharField(source='business_details_id.open_time')
    # close_time = serializers.CharField(source='business_details_id.close_time')
    # price_status= serializers.CharField(source='business_details_id.price_status')

    class Meta:
        """Meta Class"""

        model = Services
        fields = '__all__'


class ServicePriceSerializers(serializers.ModelSerializer):
    minutes = serializers.ReadOnlyField(source='duration_time.duration')
    class Meta:
        """Meta Class"""

        model = Service_price
        fields = '__all__'





class Business_Details_SeoSerializers(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = Business_Details_Seo
        fields = ('id','meta_keyword','met_title','title','meta_description','status','business_details_id')



class Business_faqSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = Business_faq
        fields = '__all__'



class ServiceSerializers2(serializers.ModelSerializer):
    # categorys=CategorySerializer1(many=True,read_only=True)
    # categorys  = serializers.CharField(source='category_id.category_name')
    class Meta:
        """Meta Class"""

        
        
        model = Services
        fields = "__all__"

class ServiceSerializers1(serializers.ModelSerializer):
    # businessgallery = serializers.CharField(source='businessgalery.image_gallery')
    business_name  = serializers.CharField(source='business_details_id.business_name')
    category_id  = serializers.CharField(source='category_id.category_name')
    address  = serializers.CharField(source='business_details_id.address')
    city =serializers.CharField(source='business_details_id.city')
    pincode =serializers.CharField(source='business_details_id.pincode')
    state =serializers.CharField(source='business_details_id.state')
    # shop_img =serializers.CharField(source='business_details_id.state')
    slug=serializers.CharField(source='business_details_id.slug')
    business_logo=serializers.CharField(source='business_details_id.business_logo.url')
    meta_keyword=serializers.CharField(source='business_details_id.meta_keyword')
    meta_title=serializers.CharField(source='business_details_id.meta_title')
    meta_description=serializers.CharField(source='business_details_id.meta_description')
    meta_tags=serializers.CharField(source='business_details_id.meta_tags')
    # business_img  = serializers.CharField(source='business_details_id.address')
    map_url = serializers.CharField(source='business_details_id.map_url')
    pan_no= serializers.CharField(source='business_details_id.pan_no')
    open_time = serializers.CharField(source='business_details_id.open_time')
    close_time = serializers.CharField(source='business_details_id.close_time')
    business_status= serializers.CharField(source='business_details_id.business_status')

    class Meta:
        """Meta Class"""

        model = Services
        fields = ('id','service_name','business_name','category_id','address','map_url','slug','open_time','pan_no','close_time','business_logo','meta_keyword','meta_title','meta_description','meta_tags','business_status','city','pincode','state')





class CartSerializers(serializers.Serializer):
    business = serializers.CharField()
    service = serializers.CharField()
    user = serializers.CharField()
    qty = serializers.CharField()
    price = serializers.CharField()

class InquirySerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = Inquiry_from
        fields = "__all__"
    def create(self, validated_data):
       
        request=self.context['request']
        location=request.data.get('location')
        category=request.data.get('category')
        business_details=request.data.get('business_details')
        inquiry=request.data.get('inquiry')
        name=request.data.get('name')
        ph=request.data.get('ph')
        email=request.data.get('email')
        description=request.data.get('description')
        fb_leads=request.data.get('fb_leads')
        shopmessage=Business_Details.objects.filter(city__city=location,category_id__category_name=category)
        inquirys=Business_Details.objects.filter(city__city=location,category_id__category_name=category).first()
        ########
        # Util.inquirymessage(ph,location,"kkk",1) 
      
     
        if inquiry == "all":
         for x in shopmessage:
           inquiry_val = Inquiry_from.objects.create(business_details_id_id=x.id,name=name,email=email,ph=ph,description=description)
           Notification.objects.create(Title="Inquiry",User_Type="BU",user=inquiry_val.business_details_id.Business_Owner_detail.user,status=0,Short_Desc=description)
           Notification.objects.create(Title="Inquiry",User_Type="Staff",user=inquiry_val.business_details_id.Business_Owner_detail.user,status=0,Short_Desc=description)
        
         Util.inquirymessage(ph,inquirys.city.city,inquirys.category_id.category_name,inquiry_val.id ) 
         
         return inquiry_val
        if Business_Details.objects.filter(city__city=location,category_id__category_name=category).exists():
           inquiry_val = Inquiry_from.objects.create(business_details_id_id=business_details,name=name,email=email,ph=ph,description=description)
           Notification.objects.create(Title="Inquiry",User_Type="BU",user=inquiry_val.business_details_id.Business_Owner_detail.user,status=0,Short_Desc=description)
           city=inquirys.city.city
           categorys=inquirys.category_id.category_name
          
           Util.shopmessage(inquiry_val.business_details_id.Business_Owner_detail.mobile_no,inquiry_val.id) 
          
           Util.inquirymessage(ph,city,categorys,inquiry_val.id) 
           return inquiry_val
            
        
    def update(self, instance, validated_data):
        instance.business_details_id=validated_data.get("business_details")
        instance.business_name=validated_data.get("business_name")
        instance.name=validated_data.get("name")
        instance.ph=validated_data.get("ph")
        instance.email=validated_data.get("email")
        instance.save()
        return instance 


class BlogSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = Blog
        # fields='__all__'
        fields = ('id','title','short_dsc','category','subcategory','image','date','image_caption','review_status')


class BlogDetailesSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = Blog
        # fields='__all__'
        fields = ('id','title','short_dsc','dsc','category','subcategory','image','date','image_caption','review_status')


class BlogCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = BlogCategory
        fields = "__all__"
    def create(self, validated_data):
        response =self.context['request'].data
        if response['name']:
            response = BlogCategory.objects.create(**validated_data)
            return response
        
    def update(self, instance, validated_data):
        instance.code=validated_data.get("code")
        instance.name=validated_data.get("name")
        instance.description=validated_data.get("description")
        instance.slug=validated_data.get("slug")
        instance.save()
        return instance 





# class BlogSubCategorySerializer(serializers.ModelSerializer):
    
#     class Meta:
#         """Meta Class"""

#         model = BlogSubCategory
#         fields = "__all__"
#     def create(self, validated_data):
#         response =self.context['request'].data
#         category=response.pop("category")
       
#         if response['name']:
#             response = BlogSubCategory.objects.create(category_id=category,**validated_data)
#             return response
        
#     def update(self, instance, validated_data):
#         instance.category_id=validated_data.get("category")
#         instance.code=validated_data.get("code")
#         instance.name=validated_data.get("name")
#         instance.description=validated_data.get("description")
#         instance.slug=validated_data.get("slug")
#         instance.save()
#         return instance 

    








class ContactSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta Class"""

        model = Contact
        fields = "__all__"
    def create(self, validated_data):
        city_val =self.context['request'].data
        
        
        if city_val['name']:
            city_instance = Contact.objects.create(**validated_data)
            data={'email_body':city_instance.description,'to_email':city_instance.email,'email_subject':city_instance.subject}
            Util.send_email1(data)
            return city_instance
    def update(self, instance, validated_data):
        request = self.context["request"]
        current_user = request.user
        instance.MDF_BY = current_user
        instance.city = validated_data.get("city")
        instance.city_status = validated_data.get("city_status")
        instance.MDF_BY=current_user
    




class ServicepriceSerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = Service_price
        fields = "__all__"




class FeedbackSerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = Feedback
        fields = "__all__"
    def create(self, validated_data):
        request =self.context['request']
       
        businessdetails= request.data.get('business_details_id')  # Access the value without modifying the QueryDict
       
        # The rest of your code for creating the category goes here

        if request.data.get('description'):
            cat_val =  Feedback.objects.create(business_details_id_id=businessdetails,**validated_data)
            return cat_val 
    



class SilderSerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = slider_image
        fields = ('id','image','alts')




class CategorySilderSerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = category_slider_image
        fields = "__all__"


from rest_framework_simplejwt.tokens import RefreshToken, TokenError



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            raise serializers.ValidationError({"error":"Token is expired or invalid"})
    


class SubcategorySerializers(serializers.ModelSerializer):
    category= serializers.ReadOnlyField(source='category_name.category_name')
    class Meta:
        """Meta Class"""

        model = subcategory
        fields = "__all__"




class SubcriptionsUserSerializers(serializers.ModelSerializer):

    class Meta:
        """Meta Class"""

        model = SubscribeUser
        fields = "__all__"
    def create(self, validated_data):
        request =self.context['request']
        
       
        email= request.data.get('email')  # Access the value without modifying the QueryDict
       
        # The rest of your code for creating the category goes here

        if request.data.get('email'):
            cat_val =  SubscribeUser.objects.create(email=email)
            return cat_val




class OrderTableSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Order_Table
        fields = "__all__"
    def create(self, validated_data):
        request =self.context['request']

        cart=request.data['cart']
        try:
          current_user=request.user
          print('current_user',current_user)
          register=Register.objects.get(user=current_user)

          
        except:
             pass
        
        for i in cart:
            business_id=Business_Details.objects.get(id=i['business_ID'])
            order_table= Order_Table.objects.create(guest_name=i['guest_name'],customer_id=register,appiontment_date=i['appiontment_date'],appionment_time=i['appionment_time'],merchent_id= business_id.Business_Owner_detail,business_name=i['business_Name'],business_address=i['business_address'],subtotal=i['subtotal'],tax=i['tax'],discount=i['discount'],total=i['total'])
            for x in i['CartItems']:
               services_id=Services.objects.get(id=x['service_id'])
               order_item=Order_Item.objects.create(order_id=order_table,service_id=services_id,service_name=x['service_name'],qty=x['qty'],market_price=x['market_price'],amount=x['amount'])
            return order_item
 



class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =Order_Item
        fields = "__all__"
        
    
       
      

class OrderTableItemSerializer(serializers.ModelSerializer):
    orderitem=OrderItemSerializer(many=True)
    class Meta:
        model = Order_Table
        fields = "__all__"
    