from django import forms

from swift.models import Subject,Course,Topic

class TopicForm(forms.ModelForm):
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
   

    class Meta:
        model = Topic
        fields = ["name", "course", "subject"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'course' in self.data:  # Check if 'course' field is present in the submitted form data
            course_id = int(self.data.get('course'))
            self.fields['subject'].queryset = Subject.objects.filter(course_id=course_id)
        elif self.instance.pk and self.instance.subject:
            course_id = self.instance.subject.course_id
            self.fields['subject'].queryset = Subject.objects.filter(course_id=course_id)


