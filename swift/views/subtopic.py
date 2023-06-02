from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import  View
from swift.forms.subtopic import SubtopicForm
from django.core.paginator import *
from swift.constantvariables import PAGINATION_PERPAGE
from swift.models import SubTopic,Course,Topic,Subject
from swift.helper import renderfile,is_ajax,LogUserActivity
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.db import transaction
from swift.models import CREATE,  UPDATE, SUCCESS, FAILED, DELETE, READ
from django.shortcuts import get_object_or_404




class SubtopicView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
       
      
        context = {
            'subtopic': None,
            'current_page': None,
            'course':Course.objects.all(),
            'subject':Subject.objects.all(),
            'topic':Topic.objects.all()
            
           
        }
        response = {}
        cond = {'is_active':True}
        # subtopic live search  
          
        filter_value = request.GET.get('filter')
        if filter_value:
            cond['name__icontains'] = filter_value
             
        # course search
        courses = request.GET.get('course')
        if courses:
            cond['topic__subject__course__id']=courses
                        
        #subject
        subject = request.GET.get('subject')
        if subject:
            cond['topic__subject__id']=subject

        #topic
        topic = request.GET.get('topic')
        if topic:
            cond['topic_id']=topic
 
        subtopic = SubTopic.objects.select_related('topic').filter(**cond).order_by('-id')
          
            
        
        
        page = int(request.GET.get('page', 1))


        paginator = Paginator(subtopic, PAGINATION_PERPAGE)

        try:
            subtopic = paginator.page(page)
        except PageNotAnInteger:
            subtopic = paginator.page(1)
        except EmptyPage:
            subtopic = paginator.page(paginator.num_pages)

        context['subtopic'], context['current_page'] = subtopic,page
        if is_ajax(request=request):
            response['status'] = True
            response['pagination'] = render_to_string("swift/subtopic/pagination.html",context=context,request=request)
            response['template'] = render_to_string('swift/subtopic/subtopic_list.html', context, request=request)
            return JsonResponse(response)
     
        return render(request,'swift/subtopic/index.html',context)




class SubtopicCreate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = {}
        form = SubtopicForm()
        print(form)
       
    
        context = {'form': form, 'id': 0}
        data['status'] = True
        data['title'] = 'Add Subtopic'
      
        data['template'] = render_to_string('swift/subtopic/subtopic_form.html', context, request=request)
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
    
        response = {}
        form = SubtopicForm(request.POST or None)
       
        if form.is_valid():
            try:
                # with transaction.atomic():
                    name = request.POST.get('name', None)
               
                   
                    topic = request.POST.get('topic',None)
                    lessons = request.POST.get('lessons',None)
                    objectives = request.POST.get('objectives',None)
                  
                    # CHECK THE DATA EXISTS
                    if not SubTopic.objects.filter(name=name).exists():
                        obj = SubTopic.objects.create(name=name,topic_id=topic,lessons=lessons,objectives=objectives)
                     
                       

                        # log entry
                        log_data = {}
                        log_data['module_name'] = 'subtopic'
                        log_data['action_type'] = CREATE
                        log_data['log_message'] = 'Subject Created'
                        log_data['status'] = SUCCESS
                        log_data['model_object'] = obj
                        log_data['db_data'] = {'name':name}
                      
                        

                        log_data['app_visibility'] = True
                        log_data['web_visibility'] = True
                        log_data['error_msg'] = ''
                        log_data['fwd_link'] = '/subtopic/'
                        LogUserActivity(request, log_data)

                        response['status'] = True
                        response['message'] = 'Added successfully'
                    else:
                        response['status'] = False
                        response['message'] = 'Subtopic Already exists'

            except Exception as error:
                print("hlo ",error)
                log_data = {}
                log_data['module_name'] = 'Subtopic'
                log_data['action_type'] = CREATE
                log_data['log_message'] = 'Subtopic updation failed'
                log_data['status'] = FAILED
                log_data['model_object'] = None
                log_data['db_data'] = {}
                log_data['app_visibility'] = False
                log_data['web_visibility'] = False
                log_data['error_msg'] = error
                log_data['fwd_link'] = '/subtopic/'
                LogUserActivity(request, log_data)

                response['status'] = False
                response['message'] = 'Something went wrong'
        else:
            response['status'] = False
            context = {'form': form}
            response['title'] = 'Add Subjtopic'
            response['valid_form'] = False
            response['template'] = render_to_string('swift/subtopic/subtopic_form.html', context, request=request)
        return JsonResponse(response)


# get subject  related to course_id
class RelatedDataView(View):
    def get(self, request):
        course_id = request.GET.get('course_id')
        if course_id :
            # Retrieve the subject and topic data based on the selected course and subject
            subject_options = Subject.objects.filter(course_id=course_id).values('id', 'name')
            
            data = {
                'subjects': list(subject_options)  
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=400)


# get topic related to subject_id
class RelatedTopic(View):
    def get(self, request):
        subject_id = request.GET.get('subject_id')
        if subject_id :
            # Retrieve the subject and topic data based on the selected course and subject
            topic_options = Topic.objects.filter(subject_id=subject_id).values('id', 'name')
            
            data = {
                'topics': list(topic_options)  
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=400)



# filter subject from course id in search
class SearchDropdown(View):
    def get(self, request):
        course_id = request.GET.get("course_id")
        subjects = Subject.objects.filter(course_id=course_id)
        subject_options = {subject.id: subject.name for subject in subjects}
        print(subject_options)
        return JsonResponse({"subjects": subject_options})

# filter topic from subject id in search
class SearchDropdown_topic(View):
    def get(self, request):
        subject_id = request.GET.get("subject_id")
        topics = Topic.objects.filter(subject_id=subject_id)
        topic_options = {topic.id: topic.name for topic in topics}
        print(topic_options)
        return JsonResponse({"topics": topic_options})        



class SubtopicUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        data = {}
        obj = get_object_or_404(SubTopic, id = id)
        form = SubtopicForm(instance=obj)
        context = {'form': form, 'id': id}
        data['status'] = True
        data['title'] = 'Edit Subtopic'
        data['course_id'] = obj.topic.subject.course_id
        data['subject']= obj.topic.subject_id
        data['topic_id']= obj.topic_id
        print(data)
      
        data['template'] = render_to_string('swift/subtopic/subtopic_form.html', context, request=request)
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data, response = {} , {}
        id = kwargs.get('pk', None)
        obj = get_object_or_404(SubTopic, id=id)
        previous_name = obj.name
        form = SubtopicForm(request.POST or None, instance=obj)

        if form.is_valid():
            try:
                with transaction.atomic():
                    if SubTopic.objects.filter(name__icontains=request.POST.get('name')).exclude(id=id).exists():
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
                    log_data['fwd_link'] = '/subtopic/'
                    LogUserActivity(request, log_data)

                    response['status'] = True
                    response['message'] = "Subtopic updated successfully"
                    return JsonResponse(response)
                
            except Exception as dberror:
                log_data = {}
                log_data['module_name'] = 'Subtopic'
                log_data['action_type'] = UPDATE
                log_data['log_message'] = 'Subtopic updation failed'
                log_data['status'] = FAILED
                log_data['model_object'] = None
                log_data['db_data'] = {}
                log_data['app_visibility'] = False
                log_data['web_visibility'] = False
                log_data['error_msg'] = dberror
                log_data['fwd_link'] = '/subtopic/'
                LogUserActivity(request, log_data)

                response['message'] = "Something went wrong"
                response['status'] = True
        else:
            response['status'] = False
            context = {'form': form}
            response['title'] = 'Edit Subtopic'
            response['valid_form'] = False
            response['template'] = render_to_string('swift/subtopic/subtopic_form.html', context, request=request)
            return JsonResponse(response)
        

       



#delete

class SubtopicDelete(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        response = {}
        obj = get_object_or_404(SubTopic, id = id)
        obj.is_active = False
        obj.save()

        # log entry
        log_data = {}
        log_data['module_name'] = 'Subtopic'
        log_data['action_type'] = DELETE
        log_data['log_message'] = f'Deleted Subtopic {obj.name}'
        log_data['status'] = SUCCESS
        log_data['model_object'] = None
        log_data['db_data'] = {'name':obj.name}
        log_data['app_visibility'] = True
        log_data['web_visibility'] = True
        log_data['error_msg'] = ''
        log_data['fwd_link'] = '/subtopic/'
        LogUserActivity(request, log_data)

        response['status'] = True
        response['message'] = "Subject deleted successfully"
        return JsonResponse(response)       
