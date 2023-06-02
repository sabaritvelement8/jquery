from django import forms

from swift.models import Subject,Course,Topic,SubTopic

class SubtopicForm(forms.ModelForm):
    name = forms.CharField(
        label="Title",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        error_messages={"required": "The name should not be empty"},
    )
    course = forms.ModelChoiceField(
        label="Course",
        widget=forms.Select(attrs={"class": "form-control", "id": "course-form"}),
        queryset=Course.objects.all(),
        required=True,
    )
    subject = forms.ModelChoiceField(
        label="Subject",
        widget=forms.Select(attrs={"class": "form-control", "id": "subject-form"}),
        queryset=Subject.objects.none(),
        required=True,
    )
    topic = forms.ModelChoiceField(
        label="topic",
        widget=forms.Select(attrs={"class": "form-control", "id": "topic-form"}),
        queryset=Topic.objects.none(),
        required=True,
    )
    lessons = forms.CharField(
        label="lessons",
  
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    objectives = forms.CharField(
        label="objectives",
       
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    
    
    
   

    class Meta:
        model = SubTopic
        fields = ["name", "course", "subject","topic","lessons","objectives",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         
        # Check if the form is bound (submitted)
        if self.is_bound:
            # Get the instance being edited, if available
            instance = kwargs.get('instance')

            # Check if the 'course' field is present in the form data
            if 'course' in self.data:
                course_id = self.data['course']
                subject_choices = Subject.objects.filter(course_id=course_id).values_list('id', 'name')
                self.fields['subject'].queryset = Subject.objects.filter(course_id=course_id)
                self.fields['subject'].choices = subject_choices
            elif instance and instance.course:
                # Use the instance's course to set the available choices
                course_id = instance.course_id
                subject_choices = Subject.objects.filter(course_id=course_id).values_list('id', 'name')
                self.fields['subject'].queryset = Subject.objects.filter(course_id=course_id)
                self.fields['subject'].choices = subject_choices

            # Check if the 'subject' field is present in the form data
            if 'subject' in self.data:
                subject_id = self.data['subject']
                topic_choices = Topic.objects.filter(subject_id=subject_id).values_list('id', 'name')
                self.fields['topic'].queryset = Topic.objects.filter(subject_id=subject_id)
                self.fields['topic'].choices = topic_choices
            elif instance and instance.subject:
                # Use the instance's subject to set the available choices
                subject_id = instance.subject_id
                topic_choices = Topic.objects.filter(subject_id=subject_id).values_list('id', 'name')
                self.fields['topic'].queryset = Topic.objects.filter(subject_id=subject_id)
                self.fields['topic'].choices = topic_choices