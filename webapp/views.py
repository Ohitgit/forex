from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.utils import psa
from django.shortcuts import render
# from django.contrib.gis.geos import Point

from django.db.models import F
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.core.mail import send_mail
from .utils import Util
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from itertools import chain


from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from businessapp.models import *
from .serializers import  *
from webapp import inquiry_custom_validation ,contact_custom_validation
from copy import deepcopy
from login.models import *
from rest_framework_simplejwt.tokens import AccessToken, TokenError

from webapp import common_search
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from webapp import schema_info

import requests
from django.http import JsonResponse
import random
import base64
from django.core.files.storage import default_storage
from django.db.models import Q
from businessapp.mongodb import *
from businessapp.models import BlackListedToken
from rest_framework_simplejwt.tokens import AccessToken
from login.models import *
def validate_token(request):
    # Extract the token from the Authorization header
    authorization_header = request.headers.get("Authorization")

    if not authorization_header or not authorization_header.startswith("Bearer "):
        return Response({"message": "Token is required in the Authorization header"}, status=status.HTTP_400_BAD_REQUEST)

    token = authorization_header.split(" ")[1]

    # Check if the token is blacklisted
    is_blacklisted = BlackListedToken.objects.filter(token=token).exists()

    if is_blacklisted:
        return Response({"message": "Token is blacklisted"}, status=status.HTTP_401_UNAUTHORIZED)

    # Continue with other checks if needed
    try:
        access_token = AccessToken(token)
        access_token.verify()

        # Assign the token to the request to make it accessible in other methods
        request.auth = access_token
        print("========token=====", token)
    except TokenError:
        return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)

    return None

def map_operator(operator, negate=False):
    # Map your operators to corresponding Django ORM lookups
    operator_mapping = {
        'equals': 'iexact',
        'not equals': 'iexact' if negate else 'exact',
        'contains': 'icontains',
        'not contains': 'icontains' if negate else 'contains',
        'startswith': 'istartswith',
        'endswith': 'iendswith',
        'Datetime': 'icontains',
    }
    mapped_operator = operator_mapping.get(operator, 'exact')
    return f"{'i' if negate else ''}{mapped_operator}"

def generate_queries(filters):
    or_conditions = []
    cond=[]
    for item in filters:
        field_name = item['field_name']
        operator = item['operator']
        value = item['value'][0]['value_name']

        query_condition = item.get('querycondition', 'AND')  # Default to 'AND' if not specified

        negate = operator.lower() == 'not equals'
        q_operator = map_operator(operator, negate)

        q_object = ~Q(**{f"{field_name}__{q_operator}": value}) if negate else Q(**{f"{field_name}__{q_operator}": value})

        
        or_conditions.append(q_object)
        cond.append(query_condition)
    # Combine all OR conditions into a single OR query
    or_query = Q()
    print(cond)
    if cond[0]=='OR':
        for condition in or_conditions:
            or_query |= condition
    else:
        for condition in or_conditions:
            or_query &= condition

    return or_query

    
    


class FacebookLogin(APIView):
    @psa('social:begin', 'social:complete')
    def post(self, request):
        return Response({'token': request.backend.strategy.session_get('access_token')})

class UserRegistration(APIView):
    def post(self, request):
        # Implement user registration logic here, create a new user.
        # You can use the data received from the Facebook authentication
        # to create the user account.
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)



class InquiryFormCreateView(GenericAPIView,CreateModelMixin,ListModelMixin):
    '''Register Create View'''
    serializer_class = InquirySerializer
    
    
    @ swagger_auto_schema(tags=['Inquiry'], operation_description="Inquiry  Create",
            operation_summary="Inquiry Creation", request_body=None)
    def post(self, request, *args, **kwargs):
        """Location status create"""
        
        # pos_valid = inquiry_custom_validation.valid_post(request)
        # if pos_valid is not True:
        #     return pos_valid             
        
        if self.create(request, *args, **kwargs):
            return Response({'message': inquiry_custom_validation.get_create_success_msg()}, status=status.HTTP_201_CREATED) 





msg='category does not exist'
req_name='category Name is required'
class CategoryView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """category class view"""
    model = category
    serializer_class = CategorySerializer
   
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    
    filterset_fields = ["id", "category_name","slug","category_description","image_caption","status",
                        "img_cdn","meta_keyword","met_title","meta_description","script"]
    search_fields = ["category_name","slug","category_description","image_caption","status",
                        "img_cdn","meta_keyword","met_title","meta_description","script"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["status"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ["location_id__city"]
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = category.objects.all().order_by("-id").reverse()

        print('query',query)
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['Category'], operation_description="Category list", operation_summary="Category  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET:
            pos_id = request.GET.get("id")
            if category.objects.filter(id=pos_id).exists():
                queryset = category.objects.get(id=pos_id)
                response_data = CategorySerializer(queryset)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                
            else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
        
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            res["column_list"] = self.column_list
        return Response(res)



class CategoryDetailsView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = category
    serializer_class = CategorySerializer
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "cat_name" in request.GET or "id"  in request.GET :
            # id = request.GET.get("id",None)
            cat_name = request.GET.get("cat_name",None)
            id=request.GET.get("id",None)
            
            if category.objects.filter(category_name=cat_name).exists() :
            
                queryset = category.objects.select_related('location_id').filter(category_name=cat_name)
                print('queryset',queryset)
                response_data = CategorySerializer(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)

            elif category.objects.filter(id=id).exists() :
            
                queryset = category.objects.select_related('location_id').filter(id=id)
                print('queryset',queryset)
                response_data = CategorySerializer(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)
            
            else:
                

                data = {
                           "data": [],
                        }
                return Response(data, status=status.HTTP_200_OK)


from functools import reduce
from operator import or_


def get_page_no(get_request):
    page = 1 
    if 'page' in get_request and len(get_request['page']) > 0 and get_request['page'][0] is not None and get_request['page'][0] != '':
        page = get_request['page']        
    return page

def get_offset(get_request):
    offset = 0
    if 'offset' in get_request and len(get_request['offset']) > 0 and get_request['offset'][0] is not None and get_request['offset'][0] != '':
        offset = get_request['offset']        
    return offset

def get_page_size(get_request):
    page_size = 10    
    if 'page_size' in get_request and len(get_request['page_size']) > 0 and get_request['page_size'][0] is not None and get_request['page_size'][0] != '':
        page_size = get_request['page_size']
    return page_size

from rest_framework.pagination import LimitOffsetPagination
class Business_DetailsView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Business_Details
    serializer_class = Business_DetailsSerializers
    filterset_fields=[]
    status_fields=[]
    ordering=[]   
    other_fields=[]
    date_fields=[]
    filterset_fields=[]
    pagination_class = LimitOffsetPagination
    def get(self, request, *args, **kwargs):

        """Position  get"""
        
        response = {}
        
        if "cat" in request.GET :
            cat = request.GET.get("cat")
            
            location = request.GET.get("location")
           
            if Business_Details.objects.filter(city__city=location,category_id__category_name=cat).exists():
                paginator = self.pagination_class()
                queryset= Business_Details.objects.select_related('category_id','city').filter(city__city=location,category_id__category_name=cat).order_by('business_status')
                category_data1=Location_Seo.objects.select_related('category_id','location_id').filter(category_id__category_name=cat,location_id__city=location)
                category_data=LocationseoSerializer(category_data1,many=True).data
                result_page = paginator.paginate_queryset(queryset, request)
                business_details= Business_DetailsSerializers(result_page,many=True).data
                res = {'category_data': category_data, 'business_details': business_details}
                response['data'] = res
                response["total_data"] = Business_Details.objects.select_related('category_id').filter(city__city=location,category_id__category_name=cat).order_by('business_status').count()
                response["total"]=queryset.count()
                return Response(response, status=status.HTTP_200_OK)
            elif Services.objects.filter(city__city=location,service_name=cat).exists():
            
                queryset2= Services.objects.select_related('category_id').filter(city__city=location,service_name__icontains=cat).order_by('business_details_id__business_status')
               
                category_data1=Location_Seo.objects.select_related('category_id','location_id').filter(category_id__category_name=cat,location_id__city=location)
                category_data=LocationseoSerializer(category_data1,many=True).data
                business_details=  ServiceSerializers1(queryset2,many=True).data
                res = {'category_data': category_data, 'business_details': business_details}
                response['data'] = res
                
                return Response(response, status=status.HTTP_200_OK)
            else:
                data = {
                           "data": [],
                        }
                return Response(data, status=status.HTTP_200_OK)
            



from django.db.models import Avg
class CategoryandLocactionView(CreateModelMixin, ListModelMixin, GenericAPIView):
    model = Business_Details
    serializer_class = Business_DetailsSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        response = {}
        res={}
        if "searchfield" in request.GET :
            cat = request.GET.get("searchfield")
            
            location = request.GET.get("location")
            print('-----------cat',cat,location)
            if Business_Details.objects.filter(city__city=location,category_id__category_name=cat).exists():
               
                queryset= Business_Details.objects.select_related('city','category_id').only('id','business_logo','business_name','open_time','close_time','city','business_status','category_id').filter(city__city=location,category_id__category_name=cat).order_by(F('business_status'))
               
                business_details= Business_DetailsSerializers(queryset,many=True).data
               
                try:
                    
                    feedback=Feedbacks.objects.filter(business_id__in=[ x.id for x in queryset])
                    
                   
                    fedbacksum=sum( [ int(i.rating) for i in feedback])
                    
                    ratings=fedbacksum/len(feedback)
                    ids={i.business_id for i in feedback}
                    print('ids55555555555555555',ids)
                    for business_detail in business_details:
                         for i in feedback:
                           if str(business_detail['id']) in ids:
                            
                               business_detail['ratings'] = ratings
                               business_detail['total']=fedbacksum
                           else:
                              business_detail['ratings'] = 0.0
                              business_detail['total']=0.0
                except Exception as e:
                     print('errrror',e)
                    
                   
               
               
                # print('queryset------------------------------',queryset1)
                
                
                
                category_data1=Location_Seo.objects.select_related('category_id','location_id').prefetch_related('category_id','location_id').only('id','meta_keyword','met_title','og_image','category_id','location_id').filter(category_id__category_name=cat,location_id__city=location)
                category_data=LocationseoSerializer(category_data1,many=True).data
               
               
               
                res = {'category_data': category_data, 'business_details':  business_details}
               
                response['data'] = res
              
                return Response(response, status=status.HTTP_200_OK)
            elif Services.objects.filter(city__city=location,service_name__icontains=cat).exists():
            
            
                queryset2= Services.objects.select_related('category_id','city').filter(city__city=location,service_name__icontains=cat).order_by('business_details_id__business_status')
                
                print('queryset',queryset2)
                category_data1=Location_Seo.objects.select_related('category_id','location_id').filter(category_id__category_name=cat,location_id__city=location)
                category_data=LocationseoSerializer(category_data1,many=True).data
                business_details = ServiceSerializers1(queryset2,many=True).data
                res = {'category_data': category_data, 'business_details': business_details}
                response['data'] = res
                # data = {
                #            "data": response_data.data,
                #         }
                return Response(response, status=status.HTTP_200_OK)
            else:
                data = {
                           "data": [],
                        }
                return Response(data, status=status.HTTP_200_OK)
                

class ContactFormCreateView(GenericAPIView,CreateModelMixin,ListModelMixin):
    '''Register Create View'''
    serializer_class = ContactSerializer
    
    
    @ swagger_auto_schema(tags=['Contact'], operation_description="Contact  Create",
            operation_summary="Contact Creation", request_body=None)
    def post(self, request, *args, **kwargs):
        """Location status create"""

        # pos_valid = inquiry_custom_validation.valid_post(request)
        # if pos_valid is not True:
        #     return pos_valid             
        
        if self.create(request, *args, **kwargs):
            return Response({'message': contact_custom_validation.get_create_success_msg()}, status=status.HTTP_201_CREATED)





   




class BusinessOwnerUpdateViews(UpdateModelMixin, RetrieveModelMixin, GenericAPIView):
    print('okk446644') 
    '''Location Views Class '''
    serializer_class =  UpdateRegisterProfileSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    lookup_url_kwarg = "id"

    def get_queryset(self): 
        print('okk4444')       
        pos_id = self.kwargs.get(self.lookup_url_kwarg)
        query =  Register.objects.filter(
            id=pos_id)
        return query

    @ swagger_auto_schema(tags=['UpdateUser Profile'], manual_parameters=None, operation_description="UpdateUser Update",
        operation_summary="UpdateUser Modify", request_body=None)
    
    def put(self, request, *args, **kwargs):
        validation_result = validate_token(request)
        if validation_result:
            return validation_result
        '''Location  update'''
        pos_id = self.kwargs.get(self.lookup_url_kwarg)
        
        if not  Register.objects.filter(id=pos_id).exists():
            return Response({'message': msg}, status=status.HTTP_404_NOT_FOUND)
        return self.update(request, *args, **kwargs)







class BusinessOwnerViews(CreateModelMixin, ListModelMixin, GenericAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    @swagger_auto_schema(tags=['Business Owner'], operation_description="Business owner list", operation_summary="Business Owner  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
        res = {}
        validation_result = validate_token(request)
        if validation_result:
            return validation_result
        queryset = Register.objects.get(user_id=request.user)
        
        response_data = UpdateRegisterProfileSerializers(queryset)
        res["data"] = response_data.data
        return Response(res)
 

class LocationView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = location
    serializer_class = LocationSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "city","city_status"]
    search_fields = ["city_status", "city"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["city_status"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = []
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = location.objects.all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['Location'], operation_description="Location list", operation_summary="Location  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET:
            pos_id = request.GET.get("id")
            if location.objects.filter(id=pos_id).exists():
                queryset = location.objects.get(id=pos_id)
                response_data = LocationSerializer(queryset)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                
            else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            
            
            res["column_list"] = self.column_list
        return Response(res)






class ServiceView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Business_Details
    serializer_class = Business_DetailsSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
            
        res = {}
        if "id" in request.GET :
            id = request.GET.get("id")
           
            if Business_Details.objects.filter(id=id).exists():
                queryset = Business_Details.objects.filter(id=id).first()
                
                # create_mongo_data(queryset.id,data=None)
                
                # print('queryset',queryset)
                response_data = ServicesBusinessDetailsSerializers(queryset)
                # business_data = {
                #            "data": response_data.data,
                #         }
                banner_data=[]
                
                for ids in Services.objects.filter(business_details_id=id):
                             serialized_data = ServiceSerializers(ids).data
                             
                             service_price=[]
                             for ids1 in Service_price.objects.filter(service_id=ids.id):
                                 service_price_obj= ServicePriceSerializers(ids1).data
                                 
                                 service_price.append(service_price_obj)
                             print("=====service_price=====",service_price)
                             serialized_data['service_price']=service_price
                             banner_data.append(serialized_data)

                banner_data1=[]
                for ids1 in Business_Gallery.objects.filter(business_details_id=id):
                             serialized_data1 = BusinessGallerySerializers(ids1).data
                            #  print("Serialized data:", serialized_data1) 
                             banner_data1.append(serialized_data1)

                
                banner_data2=[]
                
                
                banner_data3=[]
                for ids2 in Business_faq.objects.filter(business_details=id):
                             print('ids2',ids2)
                             serialized_data3= Business_faqSerializer(ids2).data
                             print("Serialized data566:", serialized_data3) 
                             banner_data3.append(serialized_data3)  
                

                banner_data4=[]
                for ids2 in Business_Details_Seo.objects.filter(business_details_id=id):
                             print('ids2',ids2)
                             serialized_data3= Business_Details_SeoSerializers(ids2).data
                             print("Serialized data566:", serialized_data3) 
                             banner_data4.append(serialized_data3) 
                print('banner',banner_data3)         
                temp = deepcopy(response_data.data)
                # print('banner',len(banner_data))
                temp['service_data']=banner_data
                temp['business_gallery']=banner_data1
                # temp['service_price']=banner_data2
                temp['business_faq']=banner_data3
                temp['business_seo']=banner_data4
                # return temp
                return Response(temp, status=status.HTTP_200_OK)
            else:
                data = {
                           "data": [],
                        }
                return Response(data, status=status.HTTP_200_OK)
            
        return Response({'msg':"something went worng"}, status=status.HTTP_404_NOT_FOUND)

    



class CategoryandServicesViews(CreateModelMixin, ListModelMixin, GenericAPIView):
    
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    @swagger_auto_schema(tags=['services&category'], operation_description="services&category list", operation_summary="services&category  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
        response={}
        
        if "location" in request.GET :
            location = request.GET.get("location")
            queryset = Services.objects.filter(city__city=location).exclude(business_details_id__isnull=True)
            category_obj=category.objects.all()
            category_data= CategorySerializer(category_obj,many=True).data
            service_data = ServiceSerializers2(queryset,many=True).data
            res = {'category_data': category_data, 'service_data': service_data}
            response['data'] = res
        
        else:
             category_obj=category.objects.all()
             queryset = Services.objects.all()
             category_data= CategorySerializer(category_obj,many=True).data
             service_data = ServiceSerializers2(queryset,many=True).data
             res = {'category_data': category_data, 'service_data': service_data}
             response['data'] = res
        
        return Response(response, status=status.HTTP_200_OK)

    
# demo pupos
class CategoryandServicesViews1(CreateModelMixin, ListModelMixin, GenericAPIView):
    
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    @swagger_auto_schema(tags=['services&category'], operation_description="services&category list", operation_summary="services&category  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
        response={}
        if "location" in request.GET :
            location = request.GET.get("location")
            queryset = Services.objects.filter(business_details_id__city__city=location)
            category_obj=category.objects.all()
            category_data= CategorySerializer(category_obj,many=True).data
            service_data = ServiceSerializers2(queryset,many=True).data
        res = {'category_data': category_data, 'service_data': service_data}
        response['data'] = res
        
        return Response(response, status=status.HTTP_200_OK)

class AddCartView(CreateModelMixin, ListModelMixin, GenericAPIView):
      serializer_class = CartSerializers
      def post(self, request):
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            business= serializer.validated_data.get('business')
            service= serializer.validated_data.get('service')
            user = serializer.validated_data.get('user')
            qty= serializer.validated_data.get('qty')
            price= serializer.validated_data.get('price')
            user1 = Cart.objects.create(business_details_id=business,service_id=service,price=price,qty=qty,user_id=user)
            return Response({'message': 'Add to Cart '},status=status.HTTP_200_OK)

        
        return Response({'message': 'Something went worng '},status=status.HTTP_404_NOT_FOUND)



# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# class LogoutView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    # def post(self, request):
        
        # # try:
        # user = User.objects.get(username=request.user)
        # token = request.data["token"]
        # # Decode the to
        # # ken to get the user ID
        # # refresh_token = RefreshToken(token)
        # # refresh_token.blacklist()
        # access_token = AccessToken.for_user(user)
        # access_token.set_exp(lifetime=3)  # 300 seconds (5 minutes)
        # return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        # # except Exception as e:
            # return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# views.py


# class LogoutView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    # def post(self, request):
        # try:
            # # Blacklist all refresh tokens for the user
            # RefreshToken.for_user(request.user).blacklist()

            # return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

        # except Exception as e:
            # # Handle exceptions, e.g., token not found
            # return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

# views.py

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is already blacklisted
        if BlackListedToken.objects.filter(token=token).exists():
            return Response({"message": "Token is already blacklisted"}, status=status.HTTP_200_OK)

        # Add the token to the blacklist
        BlackListedToken.objects.create(token=token, user=request.user)

        return Response({"message": "Token added to blacklist"}, status=status.HTTP_200_OK)


class CheckTokenValidityView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"message": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # try:
            # Check if the token is blacklisted
        is_blacklisted = BlackListedToken.objects.filter(token=token).exists()

        if is_blacklisted:
            return Response({"message": "Token is blacklisted"}, status=status.HTTP_401_UNAUTHORIZED)

        # Continue with other checks if needed
        try:
            access_token = AccessToken(token)
            access_token.verify()
            
            return Response({'status': 'Token is valid'}, status=status.HTTP_200_OK)
        except TokenError:
            
            return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)

        




import boto3
class BlogView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Blog
    serializer_class = BlogSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "slug","category"]
    search_fields = ["slug", "category"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["category"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ['id',"slug"]
        

    def __init__(self):
        self.column_list = [
            
            
        ]

    def get_queryset(self):
        # query = Blog.objects.select_related('category','subcategory').prefetch_related('category','subcategory').values('id','title','short_dsc','category','subcategory','image').order_by("-id").reverse()
        query= query = Blog.objects.select_related('category','subcategory').prefetch_related('category','subcategory').all().order_by("-id").reverse()
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['Blog'], operation_description="Blog list", operation_summary="Blog  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET:
            pos_id = request.GET.get("id")
            if Blog.objects.filter(id=pos_id).exists():
                queryset = Blog.objects.get(id=pos_id)
                response_data =BlogDetailesSerializer(queryset)
                


                
              
               
                
                banner_data=[]
               
                for ids2 in Blog_Seo.objects.filter(blog_id=pos_id):
                             img=Blog_Seo.objects.get(blog_id=pos_id)
                             print('blog_seo---------',img.blog_id.image)
                      
                             
                             serialized_data3= BlogseoSerializer(ids2).data
                             print("Serialized data566:", serialized_data3) 
                            #  dsc1={"dsc":'null'}
                             
                             banner_data.append(serialized_data3)
                            #  banner_data.append(dsc1)
                
                
                # print('banner',len(banner_data))
                res = common_search.get_single_row_page_info(res, request.GET)
                
                res["data"] = response_data.data 
            
                res['blogseo']=banner_data
                res["column_list"] = self.column_list
                return Response(res, status=status.HTTP_200_OK)
                
            else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
            # Example usage
            filters = [
                {
                    "field_name": "code",
                    "moduleName": "category",
                    "operator": "iexact",
                    "table_name": "basic_info",
                    "value":[{"value_name":"xyz"}],
                    "querycondition": "AND"
                },
                {
                    "field_name": "category__name",
                    "moduleName": "category",
                    "operator": "iexact",
                    "table_name": "basic_info",
                    "value": [{"value_name":"Spa And Salon"}],
                    "querycondition": "AND"
                },
                # Add more conditions as needed...
            ]
            
            
            django_orm_query = generate_queries(filters)
            print("========django_orm_query  hh======",django_orm_query)
            if request.GET.get("filter"):
                mutable_get = request.GET.copy()
                # Add an extra key-value pair
                mutable_get["django_orm_query"] = django_orm_query
                # Execute the query and retrieve results
                results = self.model.objects.filter(django_orm_query)
                for result in results:
                    print("========result======",result)
                res = common_search.get_filter_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, mutable_get)
            else:
                res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            res["column_list"] = self.column_list
        return Response(res)

    


class FeedbackCreateView(GenericAPIView,CreateModelMixin,ListModelMixin):
    '''Register Create View'''
    serializer_class = FeedbackSerializers
    
    @ swagger_auto_schema(tags=['Feedback'], operation_description="Feedback  Create",
            operation_summary="Feedback Creation", request_body=None)
    def post(self, request, *args, **kwargs):
        """Location status create"""

        # pos_valid = blogcategory_custom_validation.valid_post(request)
        # if pos_valid is not True:
        #     return pos_valid             
        
        if self.create(request, *args, **kwargs):
            return Response({'message':"feedback created "}, status=status.HTTP_201_CREATED)







class BlogCategoryView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = BlogCategory
    serializer_class = BlogCategorySerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "code","name"]
    search_fields = ["code", "name"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["code"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ['id']
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = BlogCategory.objects.all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['BlogCategory'], operation_description="BlogCategory list", operation_summary="BlogCategory  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET:
            pos_id = request.GET.get("id")
            if BlogCategory.objects.filter(id=pos_id).exists():
                queryset = BlogCategory.objects.get(id=pos_id)
                response_data = BlogCategorySerializer(queryset)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                
            else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            
            
            res["column_list"] = self.column_list
        return Response(res)

    



class ServiceFilterView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Business_Details
    serializer_class = Business_DetailsSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "cat" in request.GET :
            cat= request.GET.get("cat")
            
            
            if Business_Details.objects.filter(category_id__category_name=cat).exists():
                queryset=Business_Details.objects.filter(category_id__category_name=cat)
                response_data = Business_DetailsSerializers(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)
            
        return Response({'msg':"something went worng"}, status=status.HTTP_404_NOT_FOUND)





class LocationFilterView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Business_Details
    serializer_class = Business_DetailsSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "location" in request.GET :
            cat= request.GET.get("location")
            
            
            if Business_Details.objects.filter(city__city=cat).exists():
                queryset=Business_Details.objects.filter(city__city=cat)
                response_data = Business_DetailsSerializers(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)
            
        return Response({'msg':"something went worng"}, status=status.HTTP_404_NOT_FOUND)




class RatingFilterView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Business_Details
    serializer_class =FeedbackSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "rating" in request.GET :
            rating= request.GET.get("rating")
            # business_id= request.GET.get("business_id")
            
            if Business_Details.objects.filter(rating=rating).exists():
                queryset=Business_Details.objects.filter(rating=rating)
                response_data = Business_DetailsSerializers(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)
            
        return Response({'msg':"something went worng"}, status=status.HTTP_404_NOT_FOUND)
        





class SilderView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = slider_image
    serializer_class = SilderSerializers
    def get(self, request, *args, **kwargs):
        """Position  get"""
        if "category" in request.GET :
            cat= request.GET.get("category")
            print('cat',cat)
            queryset=slider_image.objects.filter(category_id__category_name=cat)
            print('queryset',queryset)
            response_data = SilderSerializers(queryset,many=True)
            data = {
                           "data": response_data.data,
                        }
            return Response(data, status=status.HTTP_200_OK)
        else:
                queryset=slider_image.objects.all()
                response_data = SilderSerializers(queryset,many=True)
                data = {
                           "data": response_data.data,
                        }
                return Response(data, status=status.HTTP_200_OK)




from datetime import datetime, timedelta

class InquiryOtpView(CreateModelMixin, ListModelMixin, GenericAPIView):
    
     serializer_class = InquirySerializer
     @ swagger_auto_schema(tags=['Inquiry'], operation_description="Inquiry  Create",
            operation_summary="Inquiry Creation", request_body=None)
     def post(self, request, *args, **kwargs):
          time_limit = datetime.now() - timedelta(days=1)
          ph=request.data.get('ph')
          if  len(ph)==10:
             InquiryOtp.objects.create(phone=ph)
             inquiry_counts=InquiryOtp.objects.filter(phone=ph,timestamp__gte=time_limit)
             if inquiry_counts.count() >= 4:
               return Response({'message': 'You have reached your daily OTP request limit.'}, status=status.HTTP_200_OK)
             
             else:
                       url = "https://www.fast2sms.com/dev/bulkV2"
                       otp=random.randint(000000,999999)
                       payload = "sender_id=ARNDM&message=161987&variables_values=User|"+str(otp)+"&route=dlt&numbers="+str(ph)
                       headers = {
                   'authorization': "NksBYWlf6KEqMCtxdwJXvSDpQ4ZPjV1AhLeru3zinm8ybo9RHGkJ3VZcs6lI80DaRxriq2tufdMpvO59",
                  'Content-Type': "application/x-www-form-urlencoded",
                   'Cache-Control': "no-cache",
                       }
                       requests.request("POST", url, headers=headers, data=payload)

         
                       
                       return Response({'otp':otp},status=status.HTTP_200_OK)   
          else:
              return Response({'message':'Invalid mobile number '},status=status.HTTP_200_OK) 
        
       


                
               
              
            





class CategorySilderView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = category_slider_image
    serializer_class = CategorySilderSerializers
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    def get(self, request, *args, **kwargs):
        """Position  get"""
        if "category" in request.GET :
            cat= request.GET.get("category")
            print('cat',cat)
            queryset=category_slider_image.objects.filter(category_id__category_name=cat)
            print('queryset',queryset)
            response_data =CategorySilderSerializers(queryset,many=True)
            data = {
                           "data": response_data.data,
                        }
            return Response(data, status=status.HTTP_200_OK)
    

class TokenVerificationView(APIView):
    def post(self, request):
        
        token = request.data.get('token')
        
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token = AccessToken(token)
            access_token.verify()
            
            return Response({'status': 'Token is valid'}, status=status.HTTP_200_OK)
        except TokenError:
            
            return Response({'error': 'Token is invalid or expired'}, status=status.HTTP_401_UNAUTHORIZED)


        
class CategoryServicesView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Services
    serializer_class = ServiceSerializers
   
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "category","img_cdn"]
    search_fields = [ "order_status"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = []
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ["category"]
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = Services.objects.all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    @swagger_auto_schema(tags=['Feddback'], operation_description="Feedback list", operation_summary="Feedback List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "category" in request.GET  :

            pos_id = request.GET.get("category")
           
            

            if  Services.objects.filter(category_id=pos_id).exists():
                queryset = Services.objects.filter(category_id=pos_id)
                response_data = ServiceSerializers(queryset,many=True)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
            
          
            else:
                
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            
            
            res["column_list"] = self.column_list
        return Response(res)




class SubcategoryView(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = subcategory
    serializer_class = SubcategorySerializers
   
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "category","img_cdn"]
    search_fields = [ "order_status"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = []
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ["category"]
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = subcategory.objects.all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    @swagger_auto_schema(tags=['Feddback'], operation_description="Feedback list", operation_summary="Feedback List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "category" in request.GET:

            pos_id = request.GET.get("category")
            print(pos_id)
            if  subcategory.objects.filter(category_id=pos_id).exists():
                queryset = subcategory.objects.filter(category_id=pos_id)
                response_data = ServiceSerializers(queryset,many=True)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                
            else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        else:
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            
            
            res["column_list"] = self.column_list
        return Response(res)



from django.contrib.auth import authenticate

class ClientUserInactive(APIView):
    def post(self, request):
        
        username= request.data.get('username')
        password= request.data.get('password')
        user_type=request.data.get("user_type")
        print('username',username)
        user = authenticate(username=username, password=password)
        if user is not None:
          
            if user_type=="EMP":
               user.is_active=False
               user.save()
            return Response({'msg': 'Your Account is Inactive'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid type Account'}, status=status.HTTP_401_UNAUTHORIZED)
   
    

def redirect_original(request, short_url):
    original_url = ShortenedURL.objects.get(short_url=short_url).original_url
    print("======original_url===",original_url)
    return JsonResponse({"original_url":original_url})


    




class BlogViews(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Position class view"""
    model = Blog
    serializer_class = BlogSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "slug","category"]
    search_fields = ["slug", "category"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["category"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ['id',"slug"]
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = Blog.objects.all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['Blog'], operation_description="Blog list", operation_summary="Blog  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET:
            pos_id = request.GET.get("id")
            if Blog.objects.filter(id=pos_id).exists():
                queryset = Blog.objects.get(id=pos_id)
                response_data = BlogSerializer(queryset)
            if  Blog_Seo.objects.filter(blog_id=pos_id).exists():
                    queryset=Blog_Seo.objects.get(blog_id=pos_id)
                    serialized_data3= BlogseoSerializer(queryset)
                          
                
            res = common_search.get_single_row_page_info(res, request.GET)
            res["data"] = response_data.data
            res['blogseo']=serialized_data3.data
            res["column_list"] = self.column_list
            return Response(res, status=status.HTTP_200_OK)
                
        else:
                return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)

        






class SubcriptionsEmailCreateView(GenericAPIView,CreateModelMixin,ListModelMixin):
    '''Register Create View'''
    serializer_class = SubcriptionsUserSerializers
    
    @ swagger_auto_schema(tags=['Subcriptionemail'], operation_description="Subcriptionemail  Create",
            operation_summary="Subcriptionemail Creation", request_body=None)
    def post(self, request, *args, **kwargs):
        """Location status create"""

        # pos_valid = custom_validation.valid_post(request)
        # if pos_valid is not True:
        #     return pos_valid             
        if not request.data.get('email'):
            return Response({'message': 'email field not exists'}, status=status.HTTP_201_CREATED)

        
        if self.create(request, *args, **kwargs):
            return Response({'message':'subscription user created'}, status=status.HTTP_201_CREATED)






class OrderTableCreate(GenericAPIView,CreateModelMixin,ListModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class =OrderTableSerializer
    
    @ swagger_auto_schema(tags=['order table'], operation_description="order table Create",
            operation_summary="order table Creation", request_body=None)
    def post(self, request, *args, **kwargs):
        """order table status create"""
      
        for i in request.data.get('cart'):
            if "appiontment_date" not in i:
                return Response({'message':"appiontment_date is  required"}, status=status.HTTP_400_BAD_REQUEST)
            if "appionment_time" not in i:
                return Response({'message':"appionment_time is  required"}, status=status.HTTP_400_BAD_REQUEST)
            if "guest_name" not in i:
               return Response({'message':"guest_name is  required"}, status=status.HTTP_400_BAD_REQUEST)
            if "business_ID" not in i:
               return Response({'message':"business is  required"}, status=status.HTTP_400_BAD_REQUEST)
            for item in i['CartItems']  :
              if "service_id" not in item:
                  return Response({'message':"service is  required"}, status=status.HTTP_400_BAD_REQUEST)
              if "service_name" not in item:
                  return Response({'message':"service_name is  required"}, status=status.HTTP_400_BAD_REQUEST)

        


        if self.create(request, *args, **kwargs):
            return Response({'message':'order created  successfully...'}, status=status.HTTP_201_CREATED)
        
class OrderTableViews(CreateModelMixin, ListModelMixin, GenericAPIView):
    """Order Table Class View"""
    model = Order_Table
    serializer_class = OrderTableItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["id", "slug","category"]
    search_fields = ["slug", "category"]
    ordering_fields = "__all__"
    ordering = ["-id"]
    status_fields = ["category"]
    date_fields = ["CRT_DT", "MDF_DT"]
    other_fields = ['id',"slug"]
        

    def __init__(self):
        self.column_list = [
            {"dataField": "ID_PSN", "dataType": "string", "caption": "ID"},
            {
                "dataField": "PSN_STATUS",
                "dataType": "string",
                "caption": "Status",
            },
            {"dataField": "NM_PSN", "dataType": "string", "caption": "Name"},
            {"dataField": "DSRPT_PSN", "dataType": "string", "caption": "Description"},
            
            {
                "dataField": "CRT_DT",
                "dataType": "date",
                "caption": "Created Date & Time",
            },
            {"dataField": "CRT_BY", "dataType": "string", "caption": "Created By"},
            {
                "dataField": "MDF_DT",
                "dataType": "date",
                "caption": "Updated Date & Time",
            },
            {"dataField": "MDF_BY", "dataType": "string", "caption": "Updated By"},
            {
                "dataField": "DC_STR",
                "dataType": "date",
                "caption": "Start Date",
            },
            {
                "dataField": "DC_END",
                "dataType": "date",
                "caption": "End Date",
            },
            
        ]

    def get_queryset(self):
        query = Order_Table.objects.select_related('order_id').all().order_by("-id").reverse()
        
        return query

    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data["column_list"] = self.column_list
        return response
    
    @swagger_auto_schema(tags=['Order Table'], operation_description="Order Table list", operation_summary="Order Table  List", request_body=None)
    def get(self, request, *args, **kwargs):
        """Position  get"""
       
        res = {}
        if "id" in request.GET or "customer_id" in request.GET :
            pos_id = request.GET.get("id") 
            customer_id=request.GET.get("customer_id")
            if Order_Table.objects.filter(merchent_id=pos_id).exists():
                queryset = Order_Table.objects.select_related('merchent_id','customer_id').filter(merchent_id=pos_id)
                response_data =  OrderTableItemSerializer(queryset,many=True)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                return Response(res, status=status.HTTP_200_OK)
            
            if Order_Table.objects.filter(customer_id=customer_id).exists():
                queryset = Order_Table.objects.select_related('merchent_id','customer_id').filter(customer_id=customer_id)
                response_data =  OrderTableItemSerializer(queryset,many=True)
                res = common_search.get_single_row_page_info(res, request.GET)
                res["data"] = response_data.data
                res["column_list"] = self.column_list
                return Response(res, status=status.HTTP_200_OK)
           
            else:
                return Response({'error': 'order Not Found.....'}, status=status.HTTP_404_NOT_FOUND)

        else:
            res = common_search.get_search_value(self.model, self.serializer_class, self.filterset_fields, self.status_fields, self.date_fields, self.other_fields, self.ordering, request.GET)
            res["column_list"] = self.column_list
        return Response(res,status=status.HTTP_200_OK)
