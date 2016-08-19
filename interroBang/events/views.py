from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from urllib.parse import quote_plus  # python 3
from django.contrib.contenttypes.models import ContentType



from .forms import EventForm
from .models import Event


# Create your views here.
def event_create(request):
    command = "Post Event"
    if not request.user.is_authenticated():
        raise Http404
    form = EventForm(request.POST or None, request.FILES or None)
    title = "Post Event"
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        # message success
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect("/")
    context = {
        "form": form,
        "title": title,
        "command": command,
    }
    return render(request, "event_form.html", context)

def event_list(request):
    queryset_list = Event.objects.active()
    if request.user.is_authenticated():
        queryset_list = Event.objects.filter(user=request.user)
    context = {
        "object_list": queryset_list,
        "title": "Event List",
        "id": id,
    }
    return render(request, "event_list.html", context)

def event_detail(request, slug=None):
    instance = get_object_or_404(Event, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user == instance.user:
            raise Http404
    share_string = quote_plus(instance.content)
    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_string,
    }
    return render(request, "event_detail.html", context)

def event_update(request, slug=None):
    command = "Update Event"
    instance = get_object_or_404(Event, slug=slug)
    if not request.user == instance.user:
        raise Http404

    form = EventForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
        "command": command,
    }
    return render(request, "event_form.html", context)

def event_delete(request, slug=None):
    instance = get_object_or_404(Event, slug=slug)
    if not request.user == instance.user:
        raise Http404
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("events:list")