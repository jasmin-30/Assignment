import datetime
import json

from django.conf import settings as st
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import UserSerializer, InformationSerializer


def homePageView(request):
    context = {
        'base_url': st.BASE_URL
    }
    if request.method == "POST":

        # =================== Login =================================
        if request.POST.get('email_address') is not None:
            email = request.POST.get('email_address')
            pwd = request.POST.get('password')

            try:
                user_obj = User.objects.get(email=email)

            except User.DoesNotExist:
                messages.error(request, "Email ID does not exist. Register first.")
                return render(request, "home.html", context)

            user = authenticate(request, username=email, password=pwd)
            if user is not None:
                login(request, user)
                if user.is_admin:
                    return HttpResponseRedirect('/admin/dashboard/')
                else:
                    return HttpResponseRedirect('/dashboard/')

            else:
                messages.error(request, "Please enter valid credentials.")
                return render(request, 'home.html', context)

        # ================== Registration ============================
        if request.POST.get('email') is not None:
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            dob = str(request.POST.get('dob'))
            city = request.POST.get('city')
            pwd = request.POST.get('password')

            try:
                user = User.objects.create_user(email, password=pwd)
                print(user)
            except IntegrityError as e:
                # Integrity error means email id is already registered
                print(e)
                messages.error(request, "Email ID is already Registered. Log in with valid credentials.")
                return render(request, "home.html", context)

            try:
                user.first_name = fname
                user.last_name = lname
                user.contact = contact
                user.city = city
                dob_list = dob.split("/")
                user.DOB = datetime.datetime(int(dob_list[2]), int(dob_list[1]), int(dob_list[0]))
                user.save()
                messages.success(request, "Successfully Registered.")
                return render(request, 'home.html', context)

            except Exception as e:
                print(e)
                user.delete()
                messages.error(request, "Technical Error Occurred")
                return render(request, 'home.html', context)

    return render(request, 'home.html', context)


# ======================= Logout View =================================
def Logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


# ======================== Dashboard view ===========================
def userDashboard(request):
    context = {
        'base_url': st.BASE_URL
    }
    if request.user.is_authenticated:
        context['name'] = request.user.first_name + " " + request.user.last_name
        info_qs = Information.objects.filter(auth_id=request.user).order_by('-timestamp')
        context["info"] = info_qs
        context["count"] = info_qs.count()
        return render(request, 'user.html', context)
    else:
        messages.error(request, "Login First")
        return HttpResponseRedirect('/')


def userProfile(request):
    context = {
        'base_url': st.BASE_URL
    }
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('first_name') is not None:
                fname = request.POST.get('first_name')
                lname = request.POST.get('last_name')
                email = request.POST.get('email')
                contact = request.POST.get('contact')
                dob = request.POST.get('dob')
                date_obj = datetime.datetime.strptime(dob, "%d %b, %Y")
                city = request.POST.get('city')

                try:
                    user_obj = User.objects.get(id=request.user.id)
                    user_obj.first_name = fname
                    user_obj.last_name = lname
                    user_obj.email = email
                    user_obj.contact = contact
                    user_obj.city = city
                    user_obj.DOB = date_obj
                    user_obj.save()
                    request.user = user_obj
                    messages.success(request, "Personal Details changed successfully")

                except User.DoesNotExist:
                    messages.error(request, "User does not exist. contact developers")

                except Exception as e:
                    print(e)
                    messages.error(request, "Technical Problem Occurred")

            if request.POST.get('newpwd') is not None:
                oldpwd = request.POST.get('oldpwd')
                newpwd = request.POST.get('newpwd')
                pwd = request.user.password
                if check_password(oldpwd, pwd):
                    try:
                        user_obj = User.objects.get(id=request.user.id)
                        user_obj.set_password(str(newpwd))
                        user_obj.save()
                        update_session_auth_hash(request, user_obj)
                        messages.success(request, "Password Changed Successfully.")

                    except Exception as e:
                        print(e)
                        messages.error(request, "Error in changing password. please try again later.")

                else:
                    messages.error(request,
                                   "Old Password does not match with the one you entered. Please enter correct password.")

        context['name'] = request.user.first_name + " " + request.user.last_name
        context['user'] = request.user
        return render(request, 'profile.html', context)

    else:
        messages.error(request, "Login First")
        return HttpResponseRedirect('/')


# ================== Admin Dashboard view =============================
def adminView(request):
    context = {
        'base_url': st.BASE_URL
    }
    if request.user.is_authenticated and request.user.is_superuser:
        user_qs = User.objects.all()
        context["users"] = user_qs
        return render(request, 'admin.html', context)
    else:
        messages.error(request, "You are not registered as administrator")
        logout(request)
        return HttpResponseRedirect('/')


# ================== API Endpoints Views ===============================
# def addInfo(request):
#     if request.user.is_authenticated:
#         if request.method == "GET":
#             data = request.REQUEST
#             print(data)
#             if request.GET.get('info') is not None:
#                 info = request.GET.get('info')
#
#                 try:
#                     info_obj = Information.objects.create(auth_id=request.user, info=info)
#                     info_obj.save()
#                     data = {
#                         'msg': "Information added Successfully",
#                         'date': datetime.datetime.now().strftime("%d %B, %Y %I:%M %p")
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_200_OK)
#                 except Exception as e:
#                     print(e)
#                     data = {
#                         'error': "Error in adding Information."
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             else:
#                 data = {
#                     "error": "Data not parsed properly."
#                 }
#                 res = json.dumps(data)
#                 return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             data = {
#                 "error": "Error in parsing data."
#             }
#             res = json.dumps(data)
#             return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     else:
#         data = {
#             "error": "Login First"
#         }
#         res = json.dumps(data)
#         return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
#
#
# def editInfo(request):
#     if request.user.is_authenticated:
#         if request.method == "GET":
#             if request.GET.get('info_id') is not None:
#                 info_id = int(request.GET.get('info_id'))
#                 info = request.GET.get('info')
#
#                 try:
#                     info_obj = Information.objects.get(id=info_id)
#                     info_obj.info = info
#                     info_obj.save()
#                     data = {
#                         'msg': "Information Updated Successfully",
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_200_OK)
#                 except Exception as e:
#                     print(e)
#                     data = {
#                         'error': "Error in Updating Information."
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             else:
#                 data = {
#                     "error": "Data not parsed properly."
#                 }
#                 res = json.dumps(data)
#                 return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             data = {
#                 "error": "Error in parsing data."
#             }
#             res = json.dumps(data)
#             return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     else:
#         data = {
#             "error": "Login First"
#         }
#         res = json.dumps(data)
#         return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
#
#
# def deleteInfo(request):
#     if request.user.is_authenticated:
#         if request.method == "GET":
#             if request.GET.get('info_id') is not None:
#                 info_id = int(request.GET.get('info_id'))
#
#                 try:
#                     info_obj = Information.objects.get(id=info_id)
#                     info_obj.delete()
#                     data = {
#                         'msg': "Information Deleted Successfully",
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_200_OK)
#                 except Exception as e:
#                     print(e)
#                     data = {
#                         'error': "Error in deleting Information."
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             else:
#                 data = {
#                     "error": "Data not parsed properly."
#                 }
#                 res = json.dumps(data)
#                 return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             data = {
#                 "error": "Error in parsing data."
#             }
#             res = json.dumps(data)
#             return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     else:
#         data = {
#             "error": "Login First"
#         }
#         res = json.dumps(data)
#         return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


class InfoApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get(self, request):
        qs = Information.objects.all()
        serialized_qs = InformationSerializer(qs, many=True)
        return Response(serialized_qs.data, status=200)

    def post(self, request):
        data = request.data
        serializer = InformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Information added successfully", "id": serializer.data["id"],
                             "date": datetime.datetime.now().strftime("%d %B, %Y %I:%M %p")}, status=200)
        else:
            print(serializer.errors)
            return Response({"error": "Technical Error occurred"}, status=500)


class EditInfoApiView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [SessionAuthentication, ]

    def get_object(self, id):
        try:
            return Information.objects.get(id=id)
        except Information.DoesNotExist as e:
            return Response({"error": "Object Not Found"}, status=404)

    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = InformationSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Information Updated Successfully"}, status=200)
        else:
            print(serializer.errors)
            return Response({"error": "Error Occurred"}, status=500)

    def delete(self, request, id=None):
        try:
            instance = self.get_object(id)
            instance.delete()
            return Response({"msg": "Information Deleted Successfully"}, status=200)
        except Exception as e:
            print(e)
            return Response({"error": "Error in deleting user"}, status=500)


class UserApiView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [SessionAuthentication, ]

    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist as e:
            return Response({"error": "User Not Found"}, status=404)

    def put(self, request, id=None):
        data = request.data
        instance = self.get_object(id)
        serializer = UserSerializer(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Updated Successfully"}, status=200)
        else:
            print(serializer.errors)
            return Response({"error": "Error Occurred"}, status=500)

    def delete(self, request, id=None):
        try:
            instance = self.get_object(id)
            instance.delete()
            return Response({"msg": "User Deleted Successfully"}, status=200)
        except Exception as e:
            print(e)
            return Response({"error": "Error in deleting user"}, status=500)


class DeleteUsers(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [SessionAuthentication, ]

    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist as e:
            return Response({"error": "User Not Found"}, status=404)

    def delete(self, request):
        if request.data is not None:
            id = list(request.data.getlist('id[]'))
            for i in id:
                instance = self.get_object(i)
                instance.delete()

            return Response({"msg": "Users Deleted Successfully"}, status=200)
        else:
            return Response({"error": "Data not passed"}, status=400)

# @api_view(['PUT', ])
# def editUser(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         if request.method == "GET":
#             if request.GET.get('user_id') is not None:
#                 id = int(request.GET.get('user_id'))
#                 first_name = request.GET.get('first_name')
#                 last_name = request.GET.get('last_name')
#                 email = request.GET.get('email')
#                 contact = request.GET.get('contact')
#                 city = request.GET.get('city')
#                 dob = request.GET.get('dob')
#                 date_obj = datetime.datetime.strptime(dob, "%d %b, %Y")
#
#                 try:
#                     user_obj = User.objects.get(id=id)
#                     user_obj.first_name = first_name
#                     user_obj.last_name = last_name
#                     user_obj.email = email
#                     user_obj.contact = contact
#                     user_obj.city = city
#                     user_obj.DOB = date_obj
#
#                     user_obj.save()
#
#                     data = {
#                         "msg": "User Information updated successfully"
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_200_OK)
#
#                 except User.DoesNotExist:
#                     data = {
#                         "error": "User id is not valid."
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_404_NOT_FOUND)
#
#                 except Exception as e:
#                     print(e)
#                     data = {
#                         "error": "Technical Error Occurred"
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             else:
#                 data = {
#                     "error": "Data not parsed properly."
#                 }
#                 res = json.dumps(data)
#                 return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             data = {
#                 "error": "Error in parsing data."
#             }
#             res = json.dumps(data)
#             return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     else:
#         data = {
#             "error": "Login First"
#         }
#         res = json.dumps(data)
#         return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
#
#
# @api_view(['DELETE', ])
# def deleteUser(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#         if request.method == "GET":
#             if request.GET.get('id') is not None:
#                 id = request.GET.get('id')
#                 list_id = eval(id)
#
#                 try:
#                     for i in list_id:
#                         obj = User.objects.get(id=i)
#                         obj.delete()
#
#                     data = {
#                         "msg": "Users deleted successfully"
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_200_OK)
#
#                 except Exception as e:
#                     print(e)
#                     data = {
#                         "error": "Technical Error Occurred."
#                     }
#                     res = json.dumps(data)
#                     return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             else:
#                 data = {
#                     "error": "Data not parsed properly."
#                 }
#                 res = json.dumps(data)
#                 return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
#
#         else:
#             data = {
#                 "error": "Error in parsing data."
#             }
#             res = json.dumps(data)
#             return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#     else:
#         data = {
#             "error": "Login First"
#         }
#         res = json.dumps(data)
#         return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
