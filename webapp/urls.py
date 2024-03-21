from django.urls import path
from webapp.views import (OrderTableViews, OrderTableCreate,SubcriptionsEmailCreateView,ClientUserInactive,SubcategoryView,CategoryServicesView,InquiryOtpView,RatingFilterView,TokenVerificationView,CategorySilderView,SilderView,CategoryandServicesViews1,CategoryDetailsView,ServiceFilterView,LocationFilterView,BlogCategoryView,FeedbackCreateView,BlogView,LogoutView,AddCartView,CategoryandLocactionView,CategoryandServicesViews,ServiceView,LocationView,
                        BusinessOwnerViews,BusinessOwnerUpdateViews,InquiryFormCreateView,CategoryView,Business_DetailsView,
                        ContactFormCreateView,CheckTokenValidityView,redirect_original)


urlpatterns = [
   
    path('inquiryViews/add/',InquiryFormCreateView.as_view(),name='InquiryForm_CreateView'),
    path('contact/add/',ContactFormCreateView.as_view(),name='contact_create'),

   
    path('category/',CategoryView.as_view(),name='category_get_by_id'),
    path('categorys/<id>/',CategoryView.as_view(),name='category_get_by_id'),
    path('categorys/',CategoryDetailsView.as_view(),name='category_details'),
    path('businessdetails/',Business_DetailsView.as_view(),name='Business_Details_list_view'),
    path('categorylocaction/',CategoryandLocactionView.as_view(),name='CategoryandLocactionView'),
  
    path('locationlist/',LocationView.as_view(),name='Locationsview'),
    path('',ServiceView.as_view(),name='ServiceView'),
   
    path('businessdetails/<id>/',Business_DetailsView.as_view(),name='Business_Details_get_by_id'),
    path('CartlistView/',AddCartView.as_view(),name='ServicelistView_get_by_id'),
    path('inquiryViews/add/',InquiryFormCreateView.as_view(),name='InquiryForm_CreateView'),
    path('UserupdateProfile/<id>/',BusinessOwnerUpdateViews.as_view(),name='BusinessOwner_update_views'),
    path('Profileview/',BusinessOwnerViews.as_view(),name='Business_OwnerViewsby_id'),
    path('categoryservices/',CategoryandServicesViews.as_view(),name='category_by_services'),
    path('categoryservices1/',CategoryandServicesViews1.as_view(),name='category_by_services1'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-token/', TokenVerificationView.as_view(), name='verify_token'),
    path('check-token-validity/', CheckTokenValidityView.as_view(), name='check_token_validity'),

    path('blog/',BlogView.as_view(),name='blog'),
    path('blogcategory/',BlogCategoryView.as_view(),name='BlogCategoryView'),
    path('feedback/',FeedbackCreateView.as_view(),name='feedbackview'),
    
    path('servicefilter/',ServiceFilterView.as_view(),name="servicefilter"),
    path('locationfilter/',LocationFilterView.as_view(),name="locationfilter"),

    path('ratingfilter/',RatingFilterView.as_view(),name="ratingfilter"),
    path('sliderview/',SilderView.as_view(),name="silderview"),


    path('categorysilderview/',CategorySilderView.as_view(),name="categorysilderview"),
    path('inquiryotp',InquiryOtpView.as_view(),name="InquiryOtp"),

    path('subcategoryservices',CategoryServicesView.as_view(),name="subcategoryservice"),
    path('subcategoryview',SubcategoryView.as_view(),name="subcategoryview"),
    path('inquiry/<str:short_url>/', redirect_original, name='redirect_original'),
    path('clientuserinactive',ClientUserInactive.as_view(),name='ClientUserInactive'),

    path('subcriptionuser', SubcriptionsEmailCreateView.as_view(),name='subcriptionuser'),


    path('ordertablecreate', OrderTableCreate.as_view(),name='ordertablecreate'),
    
    path('ordertableviews/list', OrderTableViews.as_view(),name='ordertableviewslist'),
    
    
    


   
    




    
]