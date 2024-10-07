from django.shortcuts import render, redirect
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from . import models

@csrf_exempt
def create_note(request):
    if request.method == 'POST':
        data = request.POST
        content = data.get('content')
        max_visits = data.get('visits')
        expire_at = data.get('expire_at')

        if not content:
            messages.error(request, 'Content is required.')
        if not max_visits:
            messages.error(request, 'Max visits is required.')
        if not expire_at:
            messages.error(request, 'Expire date is required.')
        
        if content and max_visits and expire_at:
            expire_date = datetime.strptime(expire_at, '%Y-%m-%d').date()
            if expire_date < timezone.now().date():
                messages.error(request, 'Expire date cannot be in the past.')
                return render(request, 'index.html')
                
            note = models.Note(
                content=content,
                remaining_views=int(max_visits),
                expire_at=datetime.strptime(expire_at, '%Y-%m-%d').date()
            )
            note.save()
            link = request.build_absolute_uri(f"/secret-note/{str(note.id)}")
            return redirect(link)
    
    return render(request, 'index.html')


@csrf_exempt
def get_note(request, id):
    note = None

    try:
        note = models.Note.objects.get(pk=id)
    except models.Note.DoesNotExist:
        messages.error(request, "The note has expired or no longer exists. Please create a new one.")
        return redirect('/secret-note')    
    
    note.remaining_views -= 1
    note.save()

    if not note or note.remaining_views < 0 or timezone.now() >= note.expire_at:
        note.delete()
        messages.error(request, "The note has expired or no longer exists. Please create a new one.")
        return redirect('/secret-note')
    
    link = request.build_absolute_uri(f"/secret-note/{str(note.id)}")
    return render(request, "note_created.html", {"note": note, "link": link})
