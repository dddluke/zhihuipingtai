from django.db import models
from ckeditor.fields import RichTextField
# Create your models here.
from tinymce.models import HTMLField
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from django import forms


# from .models import MyNote
class Blog(models.Model):
    title = models.CharField(max_length=100, unique=True, default=None, null=True)
    sBlog = RichTextField(verbose_name='内容')

    def __str__(self):
        return self.title


class MyNote(models.Model):
    title = models.CharField(max_length=64, default='a default title')
    content = RichTextField(config_name='awesome_ckeditor')
    pub_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    # pub_date = models.DateField(auto_now=True)
    personal_tags = TaggableManager()

    def __str__(self):
        return self.title[0:32]


class NoteForm(forms.ModelForm):
    class Meta:
        model = MyNote
        fields = ['title', 'content', 'personal_tags']
