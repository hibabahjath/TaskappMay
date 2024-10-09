from django.shortcuts import render,redirect

from django.views.generic import View

from myapp.forms import TaskForm,RegistrationForm,SignInForm

from myapp.models import Task

from django.contrib import messages

from django import forms

from django.db.models import Q,Count

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

from myapp.decorators import signin_required

from django.utils.decorators import method_decorator

from django.views.decorators.cache import never_cache

# Create your views here.

class SignUpView(View):

    template_name="register.html"

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            User.objects.create_user(**data)

            return redirect("login")
        
        else:

            return render(request,self.template_name,{"form":form_instance})
        
class SignInView(View):

    template_name="signin.html"

    def get(self,request,*args,**kwargs):

        form_instance=SignInForm()

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=SignInForm(request.POST)

        if form_instance.is_valid():

            # extract username and password
            uname=form_instance.cleaned_data.get("username")

            pwd=form_instance.cleaned_data.get("password")

            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("task-all")
        
        return render(request,self.template_name,{"form":form_instance})

decs=[signin_required,never_cache]

@method_decorator(decs,name="dispatch")
class TaskCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=TaskForm()

        return render(request,"task_create.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=TaskForm(request.POST)

        if form_instance.is_valid:

            form_instance.instance.user=request.user

            form_instance.save()

            messages.success(request,"Task Added Successfully")

            return redirect("task-all")
        
        else:

            messages.error(request,"Failed to Add Task")

            return render(request,"task_create.html",{"form":form_instance})
        
decs=[signin_required,never_cache]

@method_decorator(decs,name="dispatch")
class TaskListView(View):

    def get(self,request,*args,**kwargs):

        search_txt=request.GET.get("search_text")

        selected_category=request.GET.get("category","all")

        if selected_category == "all":

            qs=Task.objects.filter(user=request.user)

        else:

            qs=Task.objects.filter(category=selected_category,user=request.user)

        if search_txt != None:

            qs=Task.objects.filter(user=request.user)

            qs=qs.filter(Q(title__icontains=search_txt)|Q(description__icontains=search_txt))

        return render(request,"task_list.html",{"tasks":qs,"selected":selected_category})
    
decs=[signin_required,never_cache]

@method_decorator(decs,name="dispatch")
class TaskDetailView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Task.objects.get(id=id)

        return render(request,"task_detail.html",{"task":qs})
    
@method_decorator(decs,name="dispatch")
class TaskUpdateView(View):

    def get(self,request,*args,**kwargs):

        # extract pk from kwargs
        id=kwargs.get("pk")

        # fetch task object
        task_obj=Task.objects.get(id=id)

        form_instance=TaskForm(instance=task_obj)

        # adding status field to form_instance
        form_instance.fields["status"]=forms.ChoiceField(choices=Task.status_choices,widget=forms.Select(attrs={"class":"form-control form-select"}),initial=task_obj.status)

        return render(request,"task-edit.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        task_obj=Task.objects.get(id=id)

        form_instance=TaskForm(request.POST,instance=task_obj)

        if form_instance.is_valid():

            form_instance.instance.status=request.POST.get("status")

            form_instance.save()

            messages.success(request,"Task Updated Successfully")


            return redirect('task-all')
        
        else:

            messages.error("failed to update")

            return render(request,"task-edit.html",{"form":form_instance})


    
    # def post(self,request,*args,**kwargs):

    #     # extract id from kwargs

    #     id=kwargs.get("pk")

    #     # initialize form with request.POST

    #     form_instance=TaskForm(request.POST)

    #     if form_instance.is_valid():

    #         # fetch validated data
    #         data=form_instance.cleaned_data

    #         # extract status from request.POST

    #         status=request.POST.get("status")

    #         Task.objects.filter(id=id).update(**data,status=status)

    #         return redirect('task-all')
        
    #     else:

    #         return render(request,"task-edit.html",{"form":form_instance}

decs=[signin_required,never_cache]

@method_decorator(decs,name="dispatch")        
class TaskDeleteView(View):

    def get(self,request,*args,**kwargs):

        Task.objects.get(id=kwargs.get("pk")).delete()

        messages.success(request,"Task Deleted Successfully")


        return redirect("task-all")
    

@method_decorator(signin_required,name="dispatch")
class TaskSummaryView(View):

    def get(self,request,*args,**kwargs):

        qs=Task.objects.filter(user=request.user)

        total_task_count=qs.count()

        category_summary=qs.values("category").annotate(cat_count=Count("category"))

        print(category_summary)

        status_summary=qs.values("status").annotate(status_count=Count("status"))
        print(status_summary)

        context={

            "total_task_count":total_task_count,
        
            "status_summary":status_summary,

            "category_summary":category_summary,


        }

        return render(request,"task_summary.html",context)
    
class SignOutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("login")












