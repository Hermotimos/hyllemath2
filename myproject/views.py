
from django.http import HttpResponse
import time, asyncio
from characters.models import FirstName, CharacterVersion
from asgiref.sync import sync_to_async

@sync_to_async(thread_sensitive=False)
def get_firstnames():
    time.sleep(2)
    print('prepare to get the FirstName...')
    time.sleep(2)
    qs = FirstName.objects.all() 
    print(qs)
    print('got all the FirstName!')

@sync_to_async(thread_sensitive=False)
def get_characterversions():
    print('prepare to get the CharacterVersion...')
    time.sleep(5)
    qs = CharacterVersion.objects.all()
    print(qs)
    qs = CharacterVersion.objects.all()
    print(qs)
    print('got all the CharacterVersion!')

# views

def home_view(request):
    return HttpResponse('Hello world')

async def main_view_async(request):
    start_time = time.time()
    await asyncio.gather(get_firstnames(), get_characterversions())
    total = (time.time()-start_time)
    print('total: ', total)
    return HttpResponse('async')
