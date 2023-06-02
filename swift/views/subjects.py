from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import  View
from swift.forms.subjects import SubjectsForm
from django.core.paginator import *
from swift.constantvariables import PAGINATION_PERPAGE
from swift.models import Subject,Course
from swift.helper import renderfile,is_ajax,LogUserActivity
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.db import transaction
from swift.models import CREATE,  UPDATE, SUCCESS, FAILED, DELETE, READ
from django.shortcuts import get_object_or_404




class SubjectsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
       
      
        context = {
            'subjects': None,
            'current_page': None,
            'course':Course.objects.all(),
            
           
        }
        response = {}
        cond = {'is_active':True}
            
        if 'filter' in request.GET:
            filter_value = request.GET.get('filter')
            if filter_value:
                cond['name__icontains']=filter_value
            
        if 'course' in request.GET:
            filters = request.GET.get('course')
            if filters:
                    cond['course_id']=filters
                        

        subjects = Subject.objects.select_related('course').filter(**cond).order_by('-id')
            # return JsonResponse(response)
            
        
        
        page = int(request.GET.get('page', 1))


        paginator = Paginator(subjects, PAGINATION_PERPAGE)

        try:
            subjects = paginator.page(page)
        except PageNotAnInteger:
            subjects = paginator.page(1)
        except EmptyPage:
            subjects = paginator.page(paginator.num_pages)

        context['subjects'], context['current_page'] = subjects,page
        if is_ajax(request=request):
            response['status'] = True
            response['pagination'] = render_to_string("swift/subject/pagination.html",context=context,request=request)
            response['template'] = render_to_string('swift/subject/subject_list.html', context, request=request)
            return JsonResponse(response)
        # context['form']  = SubjectsForm()
        # return renderfile(request, 'subject', 'index', context)
        return render(request,'swift/subject/index.html',context)




class SubjectCreate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = {}
        form = SubjectsForm()
       
    
        context = {'form': form, 'id': 0}
        data['status'] = True
        data['title'] = 'Add Subject'
      
        data['template'] = render_to_string('swift/subject/subject_form.html', context, request=request)
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
    
        response = {}
        form = SubjectsForm(request.POST or None)
       
        if form.is_valid():
            try:
                # with transaction.atomic():
                    name = request.POST.get('name', None)
               
                   
                    course = request.POST.get('course',None)
                    print(course)
                    # CHECK THE DATA EXISTS
                    if not Subject.objects.filter(name=name).exists():
                        obj = Subject.objects.create(name=name,course_id=course)
                     
                       

                        # log entry
                        log_data = {}
                        log_data['module_name'] = 'subject'
                        log_data['action_type'] = CREATE
                        log_data['log_message'] = 'Subject Created'
                        log_data['status'] = SUCCESS
                        log_data['model_object'] = obj
                        log_data['db_data'] = {'name':name}
                        # log_data['db_data'] = {'course':course}
                        

                        log_data['app_visibility'] = True
                        log_data['web_visibility'] = True
                        log_data['error_msg'] = ''
                        log_data['fwd_link'] = '/subject/'
                        LogUserActivity(request, log_data)

                        response['status'] = True
                        response['message'] = 'Added successfully'
                    else:
                        response['status'] = False
                        response['message'] = 'Subject Already exists'

            except Exception as error:
                print("hlo ",error)
                log_data = {}
                log_data['module_name'] = 'Subject'
                log_data['action_type'] = CREATE
                log_data['log_message'] = 'Subject updation failed'
                log_data['status'] = FAILED
                log_data['model_object'] = None
                log_data['db_data'] = {}
                log_data['app_visibility'] = False
                log_data['web_visibility'] = False
                log_data['error_msg'] = error
                log_data['fwd_link'] = '/subject/'
                LogUserActivity(request, log_data)

                response['status'] = False
                response['message'] = 'Something went wrong'
        else:
            response['status'] = False
            context = {'form': form}
            response['title'] = 'Add Subject'
            response['valid_form'] = False
            response['template'] = render_to_string('swift/subject/subject_form.html', context, request=request)
        return JsonResponse(response)


class SubjectUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        data = {}
        obj = get_object_or_404(Subject, id = id)
        form = SubjectsForm(instance=obj)
        context = {'form': form, 'id': id}
        data['status'] = True
        data['title'] = 'Edit Subject'
        data['template'] = render_to_string('swift/subject/subject_form.html', context, request=request)
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data, response = {} , {}
        id = kwargs.get('pk', None)
        obj = get_object_or_404(Subject, id=id)
        previous_name = obj.name
        form = SubjectsForm(request.POST or None, instance=obj)

        if form.is_valid():
            try:
                with transaction.atomic():
                    if Subject.objects.filter(name__icontains=request.POST.get('name')).exclude(id=id).exists():
                        response['status'] = False
                        response['message'] = "Name already exists"
                        return JsonResponse(response)
                    obj.name = request.POST.get('name' or None)
                    obj.description = request.POST.get('description' or None)
                    obj.save()

                    # log entry
                    log_data = {}
                    log_data['module_name'] = 'Subject'
                    log_data['action_type'] = UPDATE
                    log_data['log_message'] = 'Subject Updated'
                    log_data['status'] = SUCCESS
                    log_data['model_object'] = obj
                    log_data['db_data'] = {'previous_name':previous_name,'updated_name':obj.name}
                    log_data['app_visibility'] = True
                    log_data['web_visibility'] = True
                    log_data['error_msg'] = ''
                    log_data['fwd_link'] = '/subject/'
                    LogUserActivity(request, log_data)

                    response['status'] = True
                    response['message'] = "Subject updated successfully"
                    return JsonResponse(response)
                
            except Exception as dberror:
                log_data = {}
                log_data['module_name'] = 'Subject'
                log_data['action_type'] = UPDATE
                log_data['log_message'] = 'Subject updation failed'
                log_data['status'] = FAILED
                log_data['model_object'] = None
                log_data['db_data'] = {}
                log_data['app_visibility'] = False
                log_data['web_visibility'] = False
                log_data['error_msg'] = dberror
                log_data['fwd_link'] = '/subject/'
                LogUserActivity(request, log_data)

                response['message'] = "Something went wrong"
                response['status'] = True
        else:
            response['status'] = False
            context = {'form': form}
            response['title'] = 'Edit Subject'
            response['valid_form'] = False
            response['template'] = render_to_string('swift/subject/subject_form.html', context, request=request)
            return JsonResponse(response)
        

class SubjectDelete(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        response = {}
        obj = get_object_or_404(Subject, id = id)
        obj.is_active = False
        obj.save()

        # log entry
        log_data = {}
        log_data['module_name'] = 'Subject'
        log_data['action_type'] = DELETE
        log_data['log_message'] = f'Deleted Subject {obj.name}'
        log_data['status'] = SUCCESS
        log_data['model_object'] = None
        log_data['db_data'] = {'name':obj.name}
        log_data['app_visibility'] = True
        log_data['web_visibility'] = True
        log_data['error_msg'] = ''
        log_data['fwd_link'] = '/subject/'
        LogUserActivity(request, log_data)

        response['status'] = True
        response['message'] = "Subject deleted successfully"
        return JsonResponse(response)       



#delete

class SubjectDelete(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        response = {}
        obj = get_object_or_404(Subject, id = id)
        obj.is_active = False
        obj.save()

        # log entry
        log_data = {}
        log_data['module_name'] = 'Subject'
        log_data['action_type'] = DELETE
        log_data['log_message'] = f'Deleted Subject {obj.name}'
        log_data['status'] = SUCCESS
        log_data['model_object'] = None
        log_data['db_data'] = {'name':obj.name}
        log_data['app_visibility'] = True
        log_data['web_visibility'] = True
        log_data['error_msg'] = ''
        log_data['fwd_link'] = '/subject/'
        LogUserActivity(request, log_data)

        response['status'] = True
        response['message'] = "Subject deleted successfully"
        return JsonResponse(response)       







