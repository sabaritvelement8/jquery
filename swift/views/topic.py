from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import  View
from swift.forms.topic import TopicForm
from django.core.paginator import *
from swift.constantvariables import PAGINATION_PERPAGE
from swift.models import Subject,Course,Topic
from swift.helper import renderfile,is_ajax,LogUserActivity
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.db import transaction
from swift.models import CREATE,  UPDATE, SUCCESS, FAILED, DELETE, READ
from django.shortcuts import get_object_or_404



class TopicView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        course_value = Course.objects.all()
        subject_value = Subject.objects.all()

        
        context = {
            'topic': None,
            'current_page': None,
            'subject': subject_value,
            'course': course_value,
        }
        response = {}
        cond = {'is_active': True}

        #name search
        filter_value = request.GET.get('filter')
        if filter_value:
            cond['name__icontains'] = filter_value

        #subject search
        filters = request.GET.get('subject')
        if filters:
            cond['subject_id'] = filters

        #course
        courses = request.GET.get('course')
        if courses:
            cond['subject__course__id'] = courses

        topic = Topic.objects.select_related('subject').filter(**cond).order_by('-id')

        page = int(request.GET.get('page', 1))

        paginator = Paginator(topic, PAGINATION_PERPAGE)

        try:
            topic = paginator.page(page)
        except PageNotAnInteger:
            topic = paginator.page(1)
        except EmptyPage:
            topic = paginator.page(paginator.num_pages)

        context['topic'], context['current_page'] = topic, page

        if is_ajax(request=request):
            response['status'] = True
            response['pagination'] = render_to_string("swift/topic/pagination.html", context=context, request=request)
            response['template'] = render_to_string('swift/topic/topic_list.html', context, request=request)
            return JsonResponse(response)

        return render(request, 'swift/topic/index.html', context)





# create
class TopicCreate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
    
        data = {}
        form = TopicForm()

        context = {"form": form, "id": 0}
        data["status"] = True
        data["title"] = "Add Topic"
        data["template"] = render_to_string(
            "swift/topic/topic_form.html", context, request=request
        )
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        response = {}
        form = TopicForm(request.POST or None)
        
        if form.is_valid():
            try:
                # with transaction.atomic():
                name = request.POST.get("name", None)
                # course = request.POST.get("course", None)
                subject = request.POST.get("subject", None)
                # CHECK THE DATA EXISTS
                if not Topic.objects.filter(name=name).exists():
                    obj = Topic.objects.create(
                        name=name, subject_id=subject
                    )

                    # log entry
                    log_data = {}
                    log_data["module_name"] = "topic"
                    log_data["action_type"] = CREATE
                    log_data["log_message"] = "topic Created"
                    log_data["status"] = SUCCESS
                    log_data["model_object"] = obj
                    log_data["db_data"] = {"name": name}
                    # log_data['db_data'] = {'course':course}

                    log_data["app_visibility"] = True
                    log_data["web_visibility"] = True
                    log_data["error_msg"] = ""
                    log_data["fwd_link"] = "/topic/"
                    LogUserActivity(request, log_data)

                    response["status"] = True
                    response["message"] = "Added successfully"
                else:
                    response["status"] = False
                    response["message"] = "topic Already exists"

            except Exception as error:
                log_data = {}
                log_data["module_name"] = "topic"
                log_data["action_type"] = CREATE
                log_data["log_message"] = "topic updation failed"
                log_data["status"] = FAILED
                log_data["model_object"] = None
                log_data["db_data"] = {}
                log_data["app_visibility"] = False
                log_data["web_visibility"] = False
                log_data["error_msg"] = error
                log_data["fwd_link"] = "/topic/"
                LogUserActivity(request, log_data)

                response["status"] = False
                response["message"] = "Something went wrong"
        else:
            response["status"] = False
            context = {"form": form}
            response["title"] = "Add Topic"
            response["valid_form"] = False
            response["template"] = render_to_string(
                "swift/topic/topic_form.html", context, request=request
            )
        return JsonResponse(response)



# to filter subject from course id
class GetSubjectsView(View):
    def get(self, request):
        course_id = request.GET.get("course_id")
        subjects = Subject.objects.filter(course_id=course_id)
        subject_options = {subject.id: subject.name for subject in subjects}
        return JsonResponse({"subjects": subject_options})
        


# to filter subject from course id in search
class SubjectDropdown(View):
    def get(self, request):
        course_id = request.GET.get("course_id")
        subjects = Subject.objects.filter(course_id=course_id)
        subject_options = {subject.id: subject.name for subject in subjects}
        print(subject_options)
        return JsonResponse({"subjects": subject_options})


#update 
class TopicUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        data = {}
        obj = get_object_or_404(Topic, id = id)
        form = TopicForm(instance=obj)
        context = {'form': form, 'id': id}
        data['status'] = True
        data['title'] = 'Edit Topic'
        data['course_id'] = obj.subject.course_id
        data['template'] = render_to_string('swift/topic/topic_form.html', context, request=request)
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data, response = {} , {}
        id = kwargs.get('pk', None)
        obj = get_object_or_404(Topic, id=id)
        previous_name = obj.name
        form = TopicForm(request.POST or None, instance=obj)

        if form.is_valid():
            try:
                with transaction.atomic():
                    if Topic.objects.filter(name__icontains=request.POST.get('name')).exclude(id=id).exists():
                        response['status'] = False
                        response['message'] = "Name already exists"
                        return JsonResponse(response)
                    obj.name = request.POST.get('name' or None)
                    obj.description = request.POST.get('description' or None)
                    obj.save()

                    # log entry
                    log_data = {}
                    log_data['module_name'] = 'Topic'
                    log_data['action_type'] = UPDATE
                    log_data['log_message'] = 'Topic Updated'
                    log_data['status'] = SUCCESS
                    log_data['model_object'] = obj
                    log_data['db_data'] = {'previous_name':previous_name,'updated_name':obj.name}
                    log_data['app_visibility'] = True
                    log_data['web_visibility'] = True
                    log_data['error_msg'] = ''
                    log_data['fwd_link'] = '/topic/'
                    LogUserActivity(request, log_data)

                    response['status'] = True
                    response['message'] = "Topic updated successfully"
                    return JsonResponse(response)
                
            except Exception as dberror:
                log_data = {}
                log_data['module_name'] = 'Topic'
                log_data['action_type'] = UPDATE
                log_data['log_message'] = 'Topic updation failed'
                log_data['status'] = FAILED
                log_data['model_object'] = None
                log_data['db_data'] = {}
                log_data['app_visibility'] = False
                log_data['web_visibility'] = False
                log_data['error_msg'] = dberror
                log_data['fwd_link'] = '/topic/'
                LogUserActivity(request, log_data)

                response['message'] = "Something went wrong"
                response['status'] = True
        else:
            response['status'] = False
            context = {'form': form}
            response['title'] = 'Edit Topic'
            response['valid_form'] = False
            response['template'] = render_to_string('swift/topic/topic_form.html', context, request=request)
            return JsonResponse(response)




#delete

class TopicDelete(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        response = {}
        obj = get_object_or_404(Topic, id = id)
        obj.is_active = False
        obj.save()

        # log entry
        log_data = {}
        log_data['module_name'] = 'Topic'
        log_data['action_type'] = DELETE
        log_data['log_message'] = f'Deleted Topic {obj.name}'
        log_data['status'] = SUCCESS
        log_data['model_object'] = None
        log_data['db_data'] = {'name':obj.name}
        log_data['app_visibility'] = True
        log_data['web_visibility'] = True
        log_data['error_msg'] = ''
        log_data['fwd_link'] = '/topic/'
        LogUserActivity(request, log_data)

        response['status'] = True
        response['message'] = "Topic deleted successfully"
        return JsonResponse(response)       




    